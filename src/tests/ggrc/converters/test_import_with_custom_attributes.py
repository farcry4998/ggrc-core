# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

import random
import os
from os.path import abspath
from os.path import dirname
from os.path import join
from flask import json

from tests.ggrc import TestCase
from tests.ggrc.generator import GgrcGenerator

THIS_ABS_PATH = abspath(dirname(__file__))
CSV_DIR = join(THIS_ABS_PATH, 'test_csvs/')


if os.environ.get("TRAVIS", False):
  random.seed(1)  # so we can reproduce the tests if needed


class TestImportWithCustomAttributes(TestCase):

  def setUp(self):
    TestCase.setUp(self)
    self.generator = GgrcGenerator()
    self.create_custom_attributes()
    self.create_people()
    self.client.get("/login")

  def tearDown(self):
    pass

  def import_file(self, filename, dry_run=False):
    data = {"file": (open(join(CSV_DIR, filename)), filename)}
    headers = {
        "X-test-only": "true" if dry_run else "false",
        "X-requested-by": "gGRC",
    }
    response = self.client.post("/_service/import_csv",
                                data=data, headers=headers)
    self.assertEqual(response.status_code, 200)
    return json.loads(response.data)

  def create_custom_attributes(self):
    gen = self.generator.generate_custom_attribute
    gen("product", attribute_type="Text", title="normal text")
    gen("product", attribute_type="Text", title="man text", mandatory=True)
    gen("product", attribute_type="Rich Text", title="normal RT")
    gen("product", attribute_type="Rich Text", title="man RT", mandatory=True)
    gen("product", attribute_type="Date", title="normal Date")
    gen("product", attribute_type="Date", title="man Date", mandatory=True)
    gen("product", attribute_type="Checkbox", title="normal CH")
    gen("product", attribute_type="Checkbox", title="man CH", mandatory=True)
    gen("product", attribute_type="Dropdown", title="normal select",
        options="a,b,c,d")
    gen("product", attribute_type="Dropdown", title="man select",
        options="e,f,g", mandatory=True)

  def create_people(self):
    emails = [
        "user1@ggrc.com",
        "miha@policy.com",
        "someone.else@ggrc.com",
        "another@user.com",
    ]
    for email in emails:
      self.generator.generate_person({
          "name": email.split("@")[0].title(),
          "email": email,
      }, "gGRC Admin")

  def test_product_with_all_custom_attributes(self):
    filename = "product_with_all_custom_attributes.csv"
    response = self.import_file(filename)
    expected_warnings = set([
        "Line 6: man CH contains invalid data. The value will be ignored.",
        "Line 8: normal select contains invalid data. The value will be"
        " ignored.",
        "Line 10: man select contains invalid data. The value will be"
        " ignored.",
        "Line 11: normal CH contains invalid data. The value will be ignored.",
        "Line 12: man CH contains invalid data. The value will be ignored.",
        "Line 14: normal Date contains invalid data. The value will be"
        "  ignored.",
        "Line 16: man Date contains invalid data. The value will be ignored.",
        "Line 21: Owner field does not contain a valid owner. You will be"
        "  assigned as object owner.",
        "Line 22: Specified user 'kr@en.com' does not exist. That user will be"
        "  ignored.",
        "Line 22: Owner field does not contain a valid owner. You will be"
        " assigned as object owner.",
        "Line 26: Owner field does not contain a valid owner. You will be"
        " assigned as object owner.",
        "Line 27: Specified user 'user@exameuple.com' does not exist. That"
        " user will be ignored.",
        "Line 27: Owner field does not contain a valid owner. You will be"
        " assigned as object owner."
    ])

    expected_errors = set([
        "Line 6: Field man CH is required. The line will be ignored.",
        "Line 9: Field man select is required. The line will be ignored.",
        "Line 10: Field man select is required. The line will be ignored.",
        "Line 12: Field man CH is required. The line will be ignored.",
        "Line 16: Field man Date is required. The line will be ignored.",
        "Line 18: Field man RT is required. The line will be ignored.",
        "Line 20: Field man text is required. The line will be ignored.",
        "Line 28: Field Title is required. The line will be ignored."
    ])

    self.assertEqual(expected_warnings, set(response["row_warnings"]))
    self.assertEqual(expected_errors, set(response["row_errors"]))
    self.assertEqual(18, set(response["created"]))
    self.assertEqual(8, set(response["ignored"]))

    self.assertTrue(True)
