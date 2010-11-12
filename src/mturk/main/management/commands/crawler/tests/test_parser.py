# -*- coding: utf-8 -*-

import sys
import os
import unittest

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
# add upper dir to PYTHONPATH
sys.path.append(TESTS_DIR)

import parser


class ParserTest(unittest.TestCase):
    def get_html(self, fd_name):
        try:
            fd = open(os.path.join(TESTS_DIR, fd_name), 'r')
        except IOError:
            raise Exception('Test file not found: %s' % fd_name)
        return fd.read()


class TotalHitsTest(ParserTest):
    def test_total_hits_correct(self):
        html = self.get_html('mainpage.html')
        expected = 94273
        result = parser.available_hits_mainpage(html)
        self.assertEqual(result, expected)


class HitsSingleAvailableTest(ParserTest):
    pass




if __name__ == '__main__':
    unittest.main()
