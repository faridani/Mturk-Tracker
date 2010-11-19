# -*- coding: utf-8 -*-

import ssl
import logging
import urllib2
import datetime
import hashlib

import gevent
from gevent import thread

import parser
from db import dbpool, DB


log = logging.getLogger('crawler.tasks')



def _get_html(url, timeout=5):
    """Get page code using given url. If server won't response in `timeout`
    seconds, return empty string.
    """
    try:
        return urllib2.urlopen(url, timeout=timeout).read()
    except (urllib2.URLError, ssl.SSLError), e:
        log.error('%s;;%s;;%s', type(e).__name__, url, e.args)
    return ''

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

def hits_groups_info(page_nr, retry_if_empty=True):
    """Return info about every hits group from given page number"""
    url = hitsearch_url(page_nr)
    html = _get_html(url)
    rows = []
    for n, info in enumerate(parser.hits_group_listinfo(html)):
        info['page_number'] = page_nr
        info['inpage_position'] = n + 1
        rows.append(info)
    log.debug('hits_groups_info done: %s;;%s', page_nr, len(rows))
    if not rows and retry_if_empty:
        log.debug('fetch & parsing retry spawn: %s', page_nr)
        gevent.sleep(6)
        return hits_groups_info(page_nr, False)
    return rows

def hits_group_info(group_id):
    """Return info about given hits group"""
    url = group_url(group_id)
    html = _get_html(url)
    data = parser.hits_group_details(html)
    # additional fetch of example task
    iframe_src = data.get('iframe_src', None)
    if iframe_src is None:
        # if iframe_src url does not exist, we cannot fetch html and because
        # of that, return empty string
        log.info('iframe src attribute not found: %s', url)
        data['html'] = ''
    else:
        log.debug('fetching iframe source: %s;;%s', url, iframe_src)
        data['html'] = _get_html(iframe_src, 4)
    return data

def hits_groups_total():
    """Return total number of hits groups or None"""
    url = "https://www.mturk.com/mturk/findhits?match=false"
    html = _get_html(url)
    return parser.hits_group_total(html)

def process_group(hg, crawl_id):
    """Gevent worker that should process single hitgroup.

    This should write some data into database and do not return any important
    data.
    """
    conn = dbpool.getconn(thread.get_ident())
    db = DB(conn)
    try:
        hg['keywords'] = ', '.join(hg['keywords'])
        # for those hit goups that does not contain hash group, create one and
        # setup apropiate flag
        hg['group_id_hashed'] = not bool(hg.get('group_id', None))
        if hg['group_id_hashed']:
            composition = ';'.join(map(str, (
                hg['title'], hg['requester_id'], hg['time_alloted'],
                hg['reward'], hg['description'], hg['keywords'],
                hg['qualifications']))) + ';'
            hg['group_id'] = hashlib.md5(composition).hexdigest()
            log.debug('group_id not found, creating hash: %s  %s',
                    hg['group_id'], composition)

        hit_group_content_id = db.hit_group_content_id(hg['group_id'])
        if hit_group_content_id is None:
            # fresh hitgroup - create group content entry, but first add some data
            # required by hitgroup content table
            hg['occurrence_date'] = datetime.datetime.now()
            hg['first_crawl_id'] = crawl_id
            hg.update(hits_group_info(hg['group_id']))
            hit_group_content_id = db.insert_hit_group_content(hg)
            log.debug('new hit group content: %s;;%s',
                    hit_group_content_id, hg['group_id'])

        hg['hit_group_content_id'] = hit_group_content_id
        hg['crawl_id'] = crawl_id
        db.insert_hit_group_status(hg)
        conn.commit()
    except Exception:
        log.exception('process_group fail - rollback')
        conn.rollback()
    finally:
        db.curr.close()
        dbpool.putconn(conn, thread.get_ident())
