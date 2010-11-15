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


class TestParserTools(unittest.TestCase):
    def test_human_timedelta_seconds(self):
        data = (
            ('1 hour', 1 * 60 * 60),
            ('1 minute', 60),
            ('1 second', 1),
            ('1 hour 1 minute 1 second', 1 * 60 * 60 + 60 + 1),
            ('5 hours 1 minute 5 seconds', 5 * 60 * 60 + 60 + 5),
            ('31 minutes 5 seconds', 31 * 60 + 5),
        )

        for human_delta, expected in data:
            result = parser.human_timedelta_seconds(human_delta)
            self.assertEqual(result, expected)


class TestParers(ParserTest):
    def test_hits_mainpage(self):
        html = self.get_html('mainpage.html')
        expected = 94273
        result = parser.hits_mainpage(html)
        self.assertEqual(result, expected)

    def test_hits_group_details(self):
        html = self.get_html('hitsgroupdetails.html')
        expected = {
            'duration': 420,
            'iframe_src': 'https://www.proboards.com/mturk/displayHIT.cgi?assignmentId=ASSIGNMENT_ID_NOT_AVAILABLE&hitId=1I3YFA09O0UI2NHWCCS64FSVNR2AVP',
        }
        result = parser.hits_group_details(html)
        self.assertEqual(result, expected)

    def test_hits_group_details_wrong(self):
        html = '<html>fail html</html>'
        expected = {}
        result = parser.hits_group_details(html)
        self.assertEqual(result, expected)


    def test_hits_group_listinfo(self):
        html = self.get_html('hitslist.html')
        expected_results = (
            {'group_id': '1HGJYY1GNL0AO2FW8D5C1A6146R87X', 'description': 'Given a company name and postal adress try to find an email adress for the company and company website', 'title': 'Find the email address for the company and website', 'expiration_date': datetime.datetime(2010, 11, 22, 0, 0), 'qualifications': ['Total approved HITs is greater than 100', 'HIT approval rate (%) is not less than 40'], 'requester': 'Sam GONZALES', 'keywords': ['data', 'collection', 'emails'], 'requester_id': 'A3AFJ33Q00UN6W', 'reward': 0.01, 'hits_available': 27894, 'time_alloted': 1800},
            {'group_id': None, 'description': 'Describe what you see in photos of individuals.', 'title': 'Tag One Photo', 'expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is US', 'HIT approval rate (%) is not less than 95', 'Total approved HITs is greater than 50'], 'requester': 'Roger Gutman', 'keywords': ['photos', 'rating', 'pictures', 'tags'], 'requester_id': 'A1Q45SAOJDSUMG', 'reward': 0.01, 'hits_available': 6166, 'time_alloted': 600},
            {'group_id': '1S2VCFXY6ZTQO557BKWT4MND24J593', 'description': 'Please read the data and answer the questions on Fishing Reels.', 'title': 'Questions on Fishing Reels', 'expiration_date': datetime.datetime(2010, 11, 14, 0, 0), 'qualifications': ['HIT abandonment rate (%) is less than 25', 'HIT approval rate (%) is greater than 70'], 'requester': 'Amazon Requester Inc.', 'keywords': ['fishingreels', 'amazon'], 'requester_id': 'A2SBG16L92F7S4', 'reward': 0.029999999999999999, 'hits_available': 4584, 'time_alloted': 14400},
            {'group_id': '1HGW0JKGG8O4QSH6PFWXL0JQWUM71X', 'description': '\xe3\x82\xb9\xe3\x83\x97\xe3\x83\xac\xe3\x83\x83\xe3\x83\x89\xe3\x82\xb7\xe3\x83\xbc\xe3\x83\x88\xe3\x81\xab\xe4\xb8\x8a\xe5\xa0\xb4\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xe4\xbc\x9a\xe7\xa4\xbe\xe5\x90\x8d\xe3\x83\xbb\xe3\x83\x9b\xe3\x83\xbc\xe3\x83\xa0\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xef\xbc\xb5\xef\xbc\xb2\xef\xbc\xac\xe3\x81\x8c\xe8\xbc\x89\xe3\x81\xa3\xe3\x81\xa6\xe3\x81\x84\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82 \xe5\x90\x84\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xef\xbc\xa8\xef\xbc\xb0\xe3\x81\x8b\xe3\x82\x89\xe6\x8e\xa1\xe7\x94\xa8\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x80\x81\xe6\x96\xb0\xe5\x8d\x92\xe6\x8e\xa1\xe7\x94\xa8\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x82\x92\xe8\xa6\x8b\xe3\x81\xa4\xe3\x81\x91\xe3\x81\xa6\xe3\x80\x81\xef\xbc\xb5\xef\xbc\xb2\xef\xbc\xac\xe3\x82\x92\xe8\xa8\x98\xe5\x85\xa5\xe3\x81\x97\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82', 'title': '\xe4\xb8\x8a\xe5\xa0\xb4\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xe6\x8e\xa1\xe7\x94\xa8\xe6\x83\x85\xe5\xa0\xb1\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x81\xae\xe7\xa2\xba\xe8\xaa\x8d', 'expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is JP', 'Location is US', 'HIT approval rate (%) is not less than 95'], 'requester': 'GoodJob', 'keywords': ['website', 'japan', 'companies', 'Japanese', 'new', 'grad', 'data', 'collection', 'url', 'websites', 'recruiting'], 'requester_id': 'A13R4S52DQGIMJ', 'reward': 0.050000000000000003, 'hits_available': 3650, 'time_alloted': 1800},
            {'group_id': '1KLXYMNLMXYWMPKZNT6YUS1DY2P69Y', 'description': 'In this task you&#39;ll verify whether or not we have the name of a business correct. We need to be very careful with this one, the name must be exactly as the company describes itself on its website.', 'title': 'Correct Business Names', 'expiration_date': datetime.datetime(2010, 11, 19, 0, 0), 'qualifications': ['<img src="/images/bottom_left_corner_grey.gif" width=11 height=10 border=0 alt="">', '</td> <td align="right" valign="top" colspan="2" rowspan="2" height="10"><img src="/images/bottom_right_corner_grey.gif" width=11 height=10 border=0 alt="">'], 'requester': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'address', 'business', 'verification', 'research', 'internet', 'web', 'data_entry', 'dataentry'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.040000000000000001, 'hits_available': 3640, 'time_alloted': 3600},
            {'group_id': '10NEXJ4MO9D77IVMJWY4N79LVYB426', 'description': 'In this job, you will be judging images based on three criteria - quality, relevance to a provided search query, and the quality of the parent page where the image is from.    ', 'title': 'Rate Images for Quality and Relevance (may contain mature content)', 'expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is not IN'], 'requester': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'search', 'image', 'relevance'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.10000000000000001, 'hits_available': 2954, 'time_alloted': 3600},
            {'group_id': None, 'description': 'Given a search query, evaluate quality of web search results', 'title': 'Web Search Quality (rtgg22). (WARNING: This HIT may contain adult or offensive content. Worker discretion is advised.)', 'expiration_date': datetime.datetime(2010, 11, 16, 0, 0), 'qualifications': ['Total approved HITs is not less than 1000', 'Location is US', 'HIT approval rate (%) is not less than 95', 'Adult Content Qualification is 1'], 'requester': 'RelevanceQuest', 'keywords': ['search', 'engine', 'web', 'relevance', 'quality', 'queries', 'ranking'], 'requester_id': 'A8RMEN71ICE57', 'reward': 0.02, 'hits_available': 2580, 'time_alloted': 300},
            {'group_id': None, 'description': 'Rewrite a question in your own words. Then, use your own knowledge, or knowledge from the internet, to write an answer for the question. Bad questions may be skipped.', 'title': 'Rewrite, and answer a cooking related question', 'expiration_date': datetime.datetime(2010, 11, 24, 0, 0), 'qualifications': ['foodista_qual_qa is 100', 'HIT approval rate (%) is not less than 85'], 'requester': 'Mturk Foodista', 'keywords': ['cooking', 'food', 'foodie', 'website', 'data', 'search', 'writing', 'english', 'answer', 'questions'], 'requester_id': 'AVTCBILNVTV8H', 'reward': 0.050000000000000003, 'hits_available': 2328, 'time_alloted': 3660},
            {'group_id': '1WSQRQDI8IBS86W68W8EGWA744Z766', 'description': 'In this job, you will be judging images based on three criteria - quality, relevance to a provided search query, and the quality of the parent page where the image is from.    ', 'title': 'Rate Images for Quality and Relevance', 'expiration_date': datetime.datetime(2010, 11, 19, 0, 0), 'qualifications': ['Location is not IN'], 'requester': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'search', 'image', 'relevance'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.11, 'hits_available': 1993, 'time_alloted': 3600},
            {'group_id': None, 'description': 'The survey takes most workers 10 - 20 minutes to complete. You will also receive a free personality profile generated from your responses, so please answer the questions truthfully for the most accurate results! You will only be able to take this survey once. We will check our records, and if you have already taken the survey, you will not be able to take it again. Thank you!', 'title': 'Consumption and Personality Survey', 'expiration_date': datetime.datetime(2010, 11, 12, 0, 0), 'qualifications': ['Location is US', 'HIT approval rate (%) is not less than 95'], 'requester': 'Researchers', 'keywords': ['survey', 'personality', 'test'], 'requester_id': 'A3AFD0B1CJ7YFS', 'reward': 0.5, 'hits_available': 1993, 'time_alloted': 3000},
        )

        results = parser.hits_group_listinfo(html)
        iter = itertools.izip(results, expected_results)
        results_num = 0
        for result, expected in iter:
            results_num += 1
            self.assertEqual(expected, result)

        self.assertEqual(results_num, 10)

    def test_hits_group_listinfo_wrong(self):
        html = '<html>wrong html code</html>'
        expected = []
        results = list(parser.hits_group_listinfo(html))
        self.assertEqual(expected, results)


if __name__ == '__main__':
    unittest.main()
