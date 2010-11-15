# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

import urllib2

import parser


MAX_DATA = 1024 * 1024 * 8


def _get_html(url):
    """Get page code using given url. Fetch at most MAX_DATA of data"""
    return urllib2.urlopen(url).read(MAX_DATA)

def hitsearch_url(page=1):
    return 'https://www.mturk.com/mturk/viewhits?searchWords=&selectedSearchType=hitgroups&sortType=LastUpdatedTime:1&pageNumber=' + str(page) + '&searchSpec=HITGroupSearch%23T%231%2310%23-1%23T%23!%23!LastUpdatedTime!1!%23!'

def group_url(id):
   return "https://www.mturk.com/mturk/preview?groupId=%s" % id

def amazon_review_url(id):
    return "http://www.amazon.com/review/%s" % id

def hits_mainpage_total():
    """Get total available hits from mturk main page"""
    url = 'https://www.mturk.com/mturk/welcome'
    html = _get_html(url)
    return parser.hits_mainpage(html)

def hits_groups_info(page_nr):
    """Return info about every hits group from given page number"""
    url = hitsearch_url(page_nr)
    html = _get_html(url)
    rows = []
    for info in parser.hits_group_listinfo(html):
        rows.append((page_nr, info))
    return rows

def hits_group_info(group_id):
    """Return info about given hits group"""
    url = group_url(group_id)
    html = _get_html(url)
    return parser.hits_group_details(html)
