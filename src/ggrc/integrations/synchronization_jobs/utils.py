# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module provides various utils for Issue tracker integration service."""

import logging
import time

from sqlalchemy.sql import expression

from ggrc import models
from ggrc.integrations import integrations_errors
from ggrc.integrations import issues


logger = logging.getLogger(__name__)


_BATCH_SIZE = 100


def get_active_issue_info(model_name):
  """Returns stored in GGRC issue tracker info associated with model."""
  issuetracker_cls = models.IssuetrackerIssue
  return issuetracker_cls.query.filter(
    issuetracker_cls.object_type == model_name,
    issuetracker_cls.enabled == expression.true(),
    issuetracker_cls.issue_id.isnot(None),
  ).order_by(issuetracker_cls.object_id).all()


def iter_issue_batches(ids):
  """Generates a sequence of batches of issues from Issue Tracker by IDs."""
  cli = issues.Client()

  for i in xrange(0, len(ids), _BATCH_SIZE):
    chunk = ids[i:i + _BATCH_SIZE]
    logger.debug('Issue ids to process: %s', chunk)
    try:
      response = cli.search({
          'issue_ids': chunk,
          'page_size': _BATCH_SIZE,
      })
    except integrations_errors.HttpError as error:
      logger.error(
          'Unable to fetch Issue Tracker issues by IDs: %r', error)
      return

    issue_infos = {}
    response_issues = response.get('issues') or []
    for info in response_issues:
      state = info['issueState'] or {}
      issue_infos[info['issueId']] = {
          'status': state.get('status'),
          'type': state.get('type'),
          'priority': state.get('priority'),
          'severity': state.get('severity'),
      }
    if issue_infos:
      yield issue_infos


def update_issue(cli, issue_id, params, max_attempts=5, interval=1):
  """Performs issue update request."""
  attempts = max_attempts
  while True:
    attempts -= 1
    try:
      cli.update_issue(issue_id, params)
    except integrations_errors.HttpError as error:
      if error.status == 429:
        if attempts == 0:
          raise
        logger.warning(
            'The request updating ticket ID=%s was '
            'rate limited and will be re-tried: %s', issue_id, error)
        time.sleep(interval)
        continue
    break
