# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Module for CalendarEvent model."""

from ggrc import db
from ggrc.models.mixins import Base
from ggrc.models.relationship import Relatable

from sqlalchemy.ext.declarative import declared_attr


class CalendarEvent(Relatable, Base, db.Model):
  """Model representing events for Calendar API."""
  __tablename__ = 'calendar_events'

  external_event_id = db.Column(db.String)
  title = db.Column(db.String)
  description = db.Column(db.String)
  due_date = db.Column(db.Date)
  last_synced_at = db.Column(db.Date)
  attendee_id = db.Column(
      db.Integer(), db.ForeignKey('people.id'), nullable=False
  )

  @declared_attr
  def attendee(cls):  # pylint: disable=no-self-argument
    """Relationship to user referenced by attendee_id."""
    return db.relationship(
        'Person',
        primaryjoin='{0}.attendee_id == Person.id'.format(cls.__name__),
        foreign_keys='{0}.attendee_id'.format(cls.__name__),
        remote_side='Person.id',
        uselist=False,
    )

  @property
  def is_synced(self):
    """Indicates whether the event was synced or not."""
    return self.last_synced_at is not None

  @property
  def needs_sync(self):
    """Indicates should we send this event to user or not."""
    return self.attendee.profile.send_calendar_events

  def json_equals(self, event_response):
    """Checks if event is equal to json representation."""
    return (event_response['description'] == self.description and
            event_response['summary'] == self.title)
