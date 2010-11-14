# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

import urllib2

import parser


MAX_DATA = 1024 * 10


def _read_html(url):
    return urllib2.urlopen(url).read(MAX_DATA)

def hitsearch_url(page=1):
    return 'https://www.mturk.com/mturk/viewhits?selectedSearchType=hitgroups&sortType=LastUpdatedTime%3A1&&searchSpec=HITGroupSearch%23T%232%2310%23-1%23T%23!%23!LastUpdatedTime!1!%23!&pageNumber='+str(page)

def group_url(id):
   return "https://www.mturk.com/mturk/preview?groupId=%s" % id

def amazon_review_url(id):
    return "http://www.amazon.com/review/%s" % id

def hits_mainpage_total():
    """Get total available hits from mturk main page"""
    url = 'https://www.mturk.com/mturk/welcome'
    html = _read_html(url)
    return parser.available_hits_mainpage(html)

def hits_list_info(page_nr):
    """Yield info about every hits group from given page number"""
    url = hitsearch_url(page_nr)
    html = _read_html(url)
    rows = []
    for info in parser.available_hits_list(html):
        rows.append((page_nr, info))
    return rows
