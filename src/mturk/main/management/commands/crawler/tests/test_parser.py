# -*- coding: utf-8 -*-

import sys
import os
import unittest
import itertools
import datetime

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


class TestParers(ParserTest):
    def test_total_hits_correct(self):
        html = self.get_html('mainpage.html')
        expected = 94273
        result = parser.available_hits_mainpage(html)
        self.assertEqual(result, expected)

    def test_available_hits_list(self):
        html = self.get_html('hitslist.html')
        expected_results = (
            {
                'hits': 27894,
                'expiration_date': datetime.datetime(2010, 11, 22),
                'reward': 0.01,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 18),
                'hits': 6166,
                'reward': 0.01,
            },
            {
                 'expiration_date': datetime.datetime(2010, 11, 14),
                 'hits': 4584,
                 'reward': 0.03,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 18),
                'hits': 3650,
                'reward': 0.05,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 19),
                'hits': 3640,
                'reward': 0.04,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 18),
                'hits': 2954,
                'reward': 0.1,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 16),
                'hits': 2580,
                'reward': 0.02,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 24),
                'hits': 2328,
                'reward': 0.05,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 19),
                'hits': 1993,
                'reward': 0.11,
            },
            {
                'expiration_date': datetime.datetime(2010, 11, 12),
                'hits': 1993,
                'reward': 0.5,
            },
        )

        results = parser.available_hits_list(html)
        iter = itertools.izip(results, expected_results)
        results_num = 0
        for result, expected in iter:
            results_num += 1
            self.assertEqual(expected, result)

        self.assertEqual(len(expected_results), results_num)




if __name__ == '__main__':
    unittest.main()
