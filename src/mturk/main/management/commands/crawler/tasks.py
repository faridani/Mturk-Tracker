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

def hits_groups_info(page_nr, retry_if_empty=2):
    """Return info about every hits group from given page number

    If retry_if_empty is 0, do not retry to fetch hits group info.
    """
    url = hitsearch_url(page_nr)
    html = _get_html(url)
    rows = []
    for n, info in enumerate(parser.hits_group_listinfo(html)):
        info['page_number'] = page_nr
        info['inpage_position'] = n + 1
        rows.append(info)
    log.debug('hits_groups_info done: %s;;%s', page_nr, len(rows))
    if not rows and retry_if_empty:
        wait_time = 10 - (3 * retry_if_empty)
        log.debug('fetch retry for page: %s (in %ss)', page_nr, wait_time)
        gevent.sleep(wait_time)
        return hits_groups_info(page_nr, retry_if_empty - 1)
    return rows

def hits_group_info(group_id):
    """Return info about given hits group"""
    url = group_url(group_id)
    html = _get_html(url)
    data = parser.hits_group_details(html)
    # additional fetch of example task
    iframe_src = data.get('iframe_src', None)
    if iframe_src:
        log.debug('fetching iframe source: %s;;%s', url, iframe_src)
        data['html'] = _get_html(iframe_src, 4)
    elif data.get('html', None) is None:
        data['html'] = ''
    return data

def hits_groups_total():
    """Return total number of hits groups or None"""
    url = "https://www.mturk.com/mturk/findhits?match=false"
    html = _get_html(url)
    return parser.hits_group_total(html)

def process_group(hg, crawl_id, requesters, processed_groups):
    """Gevent worker that should process single hitgroup.

    This should write some data into database and do not return any important
    data.
    """
    hg['keywords'] = ', '.join(hg['keywords'])
    # for those hit goups that does not contain hash group, create one and
    # setup apropiate flag
    hg['group_id_hashed'] = not bool(hg.get('group_id', None))
    hg['qualifications'] = ', '.join(hg['qualifications'])
    if hg['group_id_hashed']:
        composition = ';'.join(map(str, (
            hg['title'], hg['requester_id'], hg['time_alloted'],
            hg['reward'], hg['description'], hg['keywords'],
            hg['qualifications']))) + ';'
        hg['group_id'] = hashlib.md5(composition).hexdigest()
        log.debug('group_id not found, creating hash: %s  %s',
                hg['group_id'], composition)

    if hg['group_id'] in processed_groups:
        # this higroup was already processed
        log.info('duplicated group: %s;;%s', crawl_id, hg['group_id'])
        return False

    conn = dbpool.getconn(thread.get_ident())
    db = DB(conn)
    try:
        hit_group_content_id = db.hit_group_content_id(hg['group_id'])
        if hit_group_content_id is None:
            # check if there's profile for current requester and if does
            # exists with non-public status, then setup non public status for
            # current hitsgroup content
            profile = requesters.get(hg['requester_id'], None)
            if profile and profile.is_public is False:
                hg['is_public'] = False
            else:
                hg['is_public'] = True
            # fresh hitgroup - create group content entry, but first add some data
            # required by hitgroup content table
            hg['occurrence_date'] = datetime.datetime.now()
            hg['first_crawl_id'] = crawl_id
            if not hg['group_id_hashed']:
                # if group_id is hashed, we cannot fetch details because we
                # don't know what the real hash is
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
    return True
