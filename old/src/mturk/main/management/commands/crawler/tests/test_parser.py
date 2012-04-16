# -*- coding: utf-8 -*-

import os
import sys
import signal
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
            ('1 hour', 1 * 60),
            ('1 minute', 1),
            ('1 second', 0),
            ('1 week', 7 * 24 * 60),
            ('1 hour 1 minute 1 second', 1 * 60 + 1),
            ('5 hours 1 minute 5 seconds', 5 * 60 + 1),
            ('31 minutes 5 seconds 4 weeks', 31 + 4 * 7 * 24 * 60),
        )

        for human_delta, expected in data:
            result = parser.human_timedelta_seconds(human_delta)
            self.assertEqual(result, expected, (result, expected, human_delta))


class TestParers(ParserTest):
    maxtimerun = 1

    def setUp(self):
        maxtimerun = self.maxtimerun

        def handler(signum, frame):
            assert False, "Took more that %s seconds!" % maxtimerun

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(maxtimerun)

    def tearDown(self):
        # SIGALRM should not affect other tests
        signal.alarm(0)

    def test_hits_mainpage(self):
        html = self.get_html('mainpage.html')
        expected = 94273
        result = parser.hits_mainpage(html)
        self.assertEqual(result, expected)

    def test_hits_group_details(self):
        html = self.get_html('hitsgroupdetails.html')
        expected = {
            'duration': 180 / 60,
            'iframe_src': 'http://ec2-184-72-229-69.compute-1.amazonaws.com/MTurk/?image_guid=c9c60940-94d0-4181-9529-6a576f6057e6&assignmentId=ASSIGNMENT_ID_NOT_AVAILABLE&hitId=1WQ0GX1PFIBMWBTRDVWS06NG9YHH3Z',
            'html': None,
        }
        result = parser.hits_group_details(html)
        self.assertEqual(result, expected)


    def test_hits_group_details_no_iframe(self):
        html = self.get_html('hitsgroupdetails2.html')
        expected = {
            'duration': 10800 / 60,
            'iframe_src': None,
            'html': '''<input type="hidden" name="state" value="ckhvUmpaeW9yc3VLZWZ3RnQyU1NVZHp2ZTkwPTIwMTAxMTE5MDY0NFVzZXIuYXV0b0FjY2VwdEVuYWJsZWR.ZmFsc2UlVXNlci50dXJrU2VjdXJlfnRydWUl">\n        <input type="hidden" name="hitId" value="1RKSES4MC85KQQN4479SES2UA1FSS0">\n        <input type="hidden" name="prevHitSubmitted" value="false">\n        <input type="hidden" name="prevRequester" value="NDB">\n        <input type="hidden" name="requesterId" value="AASI85W063U0P">\n        <input type="hidden" name="prevReward" value="USD0.20">\n        \n        \n        \n            <input type="hidden" name="hitAutoAppDelayInSeconds" value="2592000">\n        \n        \n            <input type="hidden" name="groupId" value="1SFXPD3N6SAQFP8VYWHEUZFZWX6251">\n        \n        \n        \n            <input type="hidden" name="iteratorHitsLeft" value="">\n        \n        \n            <input type="hidden" name="iteratorSearchSpec" value="">\n        \n        \n        \n\n    \n        <div align="center" style="margin-left: 100px; margin-right: 100px; margin-bottom: 10px;">\n            \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n     \n   \n       <table cellspacing="0" cellpadding="0" border="0">\n            <tr>\n                    <td align="center" nowrap>Want to work on this HIT?</td>\n                \n            </tr>\n            <tr>\n                <td valign="top" nowrap height="26" rowspan="2" align="center">\n                        <a>\n                            \n                            \n                                <input type="image" name="/accept" src="/images/accept_hit.gif" border="0">\n                            \n                        </a>\n                </td>\n                \n            </tr>\n        </table>\n    \n\n\n<script type="text/javascript">\n \n  tooltips[\'pipeline.submit.iframes.tooltip\'] = "Submit this HIT by following the Requester\'s instructions.";\n\n</script>\n\n        ''',
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
            {'group_id': '1HGJYY1GNL0AO2FW8D5C1A6146R87X', 'description': 'Given a company name and postal adress try to find an email adress for the company and company website', 'title': 'Find the email address for the company and website', 'hit_expiration_date': datetime.datetime(2010, 11, 22, 0, 0), 'qualifications': ['Total approved HITs is greater than 100', 'HIT approval rate (%) is not less than 40'], 'requester_name': 'Sam GONZALES', 'keywords': ['data', 'collection', 'emails'], 'requester_id': 'A3AFJ33Q00UN6W', 'reward': 0.01, 'hits_available': 27894, 'time_alloted': 1800 / 60},
            {'group_id': None, 'description': 'Describe what you see in photos of individuals.', 'title': 'Tag One Photo', 'hit_expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is US', 'HIT approval rate (%) is not less than 95', 'Total approved HITs is greater than 50'], 'requester_name': 'Roger Gutman', 'keywords': ['photos', 'rating', 'pictures', 'tags'], 'requester_id': 'A1Q45SAOJDSUMG', 'reward': 0.01, 'hits_available': 6166, 'time_alloted': 600 / 60},
            {'group_id': '1S2VCFXY6ZTQO557BKWT4MND24J593', 'description': 'Please read the data and answer the questions on Fishing Reels.', 'title': 'Questions on Fishing Reels', 'hit_expiration_date': datetime.datetime(2010, 11, 14, 0, 0), 'qualifications': ['HIT abandonment rate (%) is less than 25', 'HIT approval rate (%) is greater than 70'], 'requester_name': 'Amazon Requester Inc.', 'keywords': ['fishingreels', 'amazon'], 'requester_id': 'A2SBG16L92F7S4', 'reward': 0.029999999999999999, 'hits_available': 4584, 'time_alloted': 14400 / 60},
            {'group_id': '1HGW0JKGG8O4QSH6PFWXL0JQWUM71X', 'description': '\xe3\x82\xb9\xe3\x83\x97\xe3\x83\xac\xe3\x83\x83\xe3\x83\x89\xe3\x82\xb7\xe3\x83\xbc\xe3\x83\x88\xe3\x81\xab\xe4\xb8\x8a\xe5\xa0\xb4\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xe4\xbc\x9a\xe7\xa4\xbe\xe5\x90\x8d\xe3\x83\xbb\xe3\x83\x9b\xe3\x83\xbc\xe3\x83\xa0\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xef\xbc\xb5\xef\xbc\xb2\xef\xbc\xac\xe3\x81\x8c\xe8\xbc\x89\xe3\x81\xa3\xe3\x81\xa6\xe3\x81\x84\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82 \xe5\x90\x84\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xef\xbc\xa8\xef\xbc\xb0\xe3\x81\x8b\xe3\x82\x89\xe6\x8e\xa1\xe7\x94\xa8\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x80\x81\xe6\x96\xb0\xe5\x8d\x92\xe6\x8e\xa1\xe7\x94\xa8\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x82\x92\xe8\xa6\x8b\xe3\x81\xa4\xe3\x81\x91\xe3\x81\xa6\xe3\x80\x81\xef\xbc\xb5\xef\xbc\xb2\xef\xbc\xac\xe3\x82\x92\xe8\xa8\x98\xe5\x85\xa5\xe3\x81\x97\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82', 'title': '\xe4\xb8\x8a\xe5\xa0\xb4\xe4\xbc\x81\xe6\xa5\xad\xe3\x81\xae\xe6\x8e\xa1\xe7\x94\xa8\xe6\x83\x85\xe5\xa0\xb1\xe3\x83\x9a\xe3\x83\xbc\xe3\x82\xb8\xe3\x81\xae\xe7\xa2\xba\xe8\xaa\x8d', 'hit_expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is JP', 'Location is US', 'HIT approval rate (%) is not less than 95'], 'requester_name': 'GoodJob', 'keywords': ['website', 'japan', 'companies', 'Japanese', 'new', 'grad', 'data', 'collection', 'url', 'websites', 'recruiting'], 'requester_id': 'A13R4S52DQGIMJ', 'reward': 0.050000000000000003, 'hits_available': 3650, 'time_alloted': 1800 / 60},
            {'group_id': '1KLXYMNLMXYWMPKZNT6YUS1DY2P69Y', 'description': 'In this task you&#39;ll verify whether or not we have the name of a business correct. We need to be very careful with this one, the name must be exactly as the company describes itself on its website.', 'title': 'Correct Business Names', 'hit_expiration_date': datetime.datetime(2010, 11, 19, 0, 0), 'qualifications': ['<img src="/images/bottom_left_corner_grey.gif" width=11 height=10 border=0 alt="">', '</td> <td align="right" valign="top" colspan="2" rowspan="2" height="10"><img src="/images/bottom_right_corner_grey.gif" width=11 height=10 border=0 alt="">'], 'requester_name': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'address', 'business', 'verification', 'research', 'internet', 'web', 'data_entry', 'dataentry'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.040000000000000001, 'hits_available': 3640, 'time_alloted': 3600 / 60},
            {'group_id': '10NEXJ4MO9D77IVMJWY4N79LVYB426', 'description': 'In this job, you will be judging images based on three criteria - quality, relevance to a provided search query, and the quality of the parent page where the image is from.    ', 'title': 'Rate Images for Quality and Relevance (may contain mature content)', 'hit_expiration_date': datetime.datetime(2010, 11, 18, 0, 0), 'qualifications': ['Location is not IN'], 'requester_name': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'search', 'image', 'relevance'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.10000000000000001, 'hits_available': 2954, 'time_alloted': 3600 / 60},
            {'group_id': None, 'description': 'Given a search query, evaluate quality of web search results', 'title': 'Web Search Quality (rtgg22). (WARNING: This HIT may contain adult or offensive content. Worker discretion is advised.)', 'hit_expiration_date': datetime.datetime(2010, 11, 16, 0, 0), 'qualifications': ['Total approved HITs is not less than 1000', 'Location is US', 'HIT approval rate (%) is not less than 95', 'Adult Content Qualification is 1'], 'requester_name': 'RelevanceQuest', 'keywords': ['search', 'engine', 'web', 'relevance', 'quality', 'queries', 'ranking'], 'requester_id': 'A8RMEN71ICE57', 'reward': 0.02, 'hits_available': 2580, 'time_alloted': 300 / 60},
            {'group_id': None, 'description': 'Rewrite a question in your own words. Then, use your own knowledge, or knowledge from the internet, to write an answer for the question. Bad questions may be skipped.', 'title': 'Rewrite, and answer a cooking related question', 'hit_expiration_date': datetime.datetime(2010, 11, 24, 0, 0), 'qualifications': ['foodista_qual_qa is 100', 'HIT approval rate (%) is not less than 85'], 'requester_name': 'Mturk Foodista', 'keywords': ['cooking', 'food', 'foodie', 'website', 'data', 'search', 'writing', 'english', 'answer', 'questions'], 'requester_id': 'AVTCBILNVTV8H', 'reward': 0.050000000000000003, 'hits_available': 2328, 'time_alloted': 3660 / 60},
            {'group_id': '1WSQRQDI8IBS86W68W8EGWA744Z766', 'description': 'In this job, you will be judging images based on three criteria - quality, relevance to a provided search query, and the quality of the parent page where the image is from.    ', 'title': 'Rate Images for Quality and Relevance', 'hit_expiration_date': datetime.datetime(2010, 11, 19, 0, 0), 'qualifications': ['Location is not IN'], 'requester_name': 'Dolores Labs', 'keywords': ['mobmerge', 'builder', 'dolores', 'labs', 'crowd', 'flower', 'crowdflower', 'doloreslabs', 'deloreslabs', 'delores', 'search', 'image', 'relevance'], 'requester_id': 'A2IR7ETVOIULZU', 'reward': 0.11, 'hits_available': 1993, 'time_alloted': 3600 / 60},
            {'group_id': None, 'description': 'The survey takes most workers 10 - 20 minutes to complete. You will also receive a free personality profile generated from your responses, so please answer the questions truthfully for the most accurate results! You will only be able to take this survey once. We will check our records, and if you have already taken the survey, you will not be able to take it again. Thank you!', 'title': 'Consumption and Personality Survey', 'hit_expiration_date': datetime.datetime(2010, 11, 12, 0, 0), 'qualifications': ['Location is US', 'HIT approval rate (%) is not less than 95'], 'requester_name': 'Researchers', 'keywords': ['survey', 'personality', 'test'], 'requester_id': 'A3AFD0B1CJ7YFS', 'reward': 0.5, 'hits_available': 1993, 'time_alloted': 3000 / 60},
        )

        results = parser.hits_group_listinfo(html)
        iter = itertools.izip(results, expected_results)
        results_num = 0
        for result, expected in iter:
            results_num += 1
            self.assertEqual(expected, result)

        self.assertEqual(results_num, 10)

    def test_hits_group_listinfo__new_html(self):
        html = self.get_html('hitslist_new.html')
        results = list(parser.hits_group_listinfo(html))
        self.assertEqual(len(results), 10)

    def test_hits_group_listinfo_wrong(self):
        html = '<html>wrong html code</html>'
        expected = []
        results = list(parser.hits_group_listinfo(html))
        self.assertEqual(expected, results)

    def test_hits_group_total(self):
        html = self.get_html('hitslist.html')
        expected = 2076
        result = parser.hits_group_total(html)
        self.assertEqual(result, expected)

    def test_hits_group_total_wrong(self):
        html = '<html>bad html</html>'
        expected = None
        result = parser.hits_group_total(html)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
