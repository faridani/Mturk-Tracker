"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from mturk.importer.management.commands.import_hitgroups import parse_time_alloted

class ImportHitGroupsTest(TestCase):
    def test_time_alloted_parsing(self):

        self.failUnlessEqual(parse_time_alloted('4 hours 30 minutes'), 270)
        self.failUnlessEqual(parse_time_alloted('1 hours'), 60)
        self.failUnlessEqual(parse_time_alloted('30 minutes'), 30)