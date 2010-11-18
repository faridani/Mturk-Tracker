# -*- coding: utf-8 -*-

import sys

try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    sys.exit('Gevent library is required: http://www.gevent.org/')


import time
import datetime
import logging
import hashlib
from optparse import make_option

import gevent
from django.core.management.base import BaseCommand

from tenclouds.pid import Pid
from mturk.main.models import Crawl
from crawler import tasks
from crawler.db import dbpool, DB

log = logging.getLogger('crawl')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--workers', dest='workers', type='int', default=5),
    )

    def setup_logging(self):
        logging.basicConfig(filename='/tmp/mturk_crawler.log', level=logging.DEBUG)

    def handle(self, *args, **options):
        _start_time = time.time()
        self.setup_logging()
        pid = Pid('mturk_crawler', True)
        log.info('crawler started: %s;;%s', args, options)
        self.maxworkers = options['workers']
        start_time = datetime.datetime.now()

        hits_available = tasks.hits_mainpage_total()
        groups_available = tasks.hits_groups_total()

        hits = self.fetch_hits_list()
        log.debug('hit groups info fetched: %s', len(hits))

        # create crawl object that will be filled with data later
        crawl = Crawl.objects.create(
                start_time=start_time,
                end_time=datetime.datetime.now(),
                success=True,
                hits_available=hits_available,
                hits_downloaded=0,
                groups_available=groups_available,
                groups_downloaded=len(hits))
        log.debug('fresh crawl object created: %s', crawl.id)

        # manage database connections here - should be one for each
        # task working at the same time
        jobs = []
        for hg in hits:
            jobs.append(gevent.Greenlet(process_group, hg, crawl))
            if len(jobs) < self.maxworkers:
                continue

            log.debug('processing pack of hitgroups objects')
            [j.start() for j in jobs]
            gevent.joinall(jobs, timeout=20)
            # check if all jobs ended successfully
            for job in jobs:
                if not job.ready():
                    log.error('Killing job: %s', job)
                    job.kill()

            jobs = []

        log.debug('processing last pack of hitgroups objects')
        [j.start() for j in jobs]
        gevent.joinall(jobs)
        dbpool.closeall()

        work_time = time.time() - _start_time
        log.info('processed objects: %s', len(hits))
        log.info('done: %.2f', work_time)

    def fetch_hits_list(self):
        hits = []

        counter = count(1, self.maxworkers)
        for i in counter:
            jobs = []
            for page_nr in range(i, i + self.maxworkers):
                jobs.append(gevent.Greenlet(tasks.hits_groups_info, page_nr))
            [j.start() for j in jobs]
            gevent.joinall(jobs)

            # get data from completed tasks & remove empty results
            data = []
            for job in jobs:
                if job.value:
                    data.extend(job.value)

            # if no data was returned, end - previous page was probably the
            # last one with results
            if not data:
                break
            hits.extend(data)

        return hits

def count(firstval=0, step=1):
    "Port of itertools.count from python2.7"
    while True:
        yield firstval
        firstval += step

def process_group(hg, crawl):
    """Gevent worker that should process single hitgroup.

    This should write some data into database and do not return any important
    data.
    """
    conn = dbpool.getconn()
    db = DB(conn)
    hg['keywords'] = ', '.join(hg['keywords'])
    # for those hit goups that does not contain hash group, create one and
    # setup apropiate flag
    hg['group_id_hashed'] = bool(hg.get('group_id', None))
    if not hg['group_id_hashed']:
        composition = ';'.join(map(str, (
            hg['title'], hg['requester_id'], hg['time_alloted'],
            hg['reward'], hg['description'], hg['keywords'],
            hg['qualifications']))) + ';'
        hg['group_id'] = hashlib.md5(composition).hexdigest()
        log.debug('group_id not found, creating hash: %s', hg['group_id'])

    hit_group_content_id = db.hit_group_content_id(hg['group_id'])
    if hit_group_content_id is None:
        # fresh hitgroup - create group content entry, but first add some data
        # required by hitgroup content table
        hg['occurrence_date'] = crawl.start_time
        hg['first_crawl_id'] = crawl.id
        hg.update(tasks.hits_group_info(hg['group_id']))
        hg['fist_crawl_id'] = crawl.id
        db.insert_hit_group_content(hg)
        hit_group_content_id = db.hit_group_content_id(hg['group_id'])
        log.info('new hit group content: %s;;%s',
                hit_group_content_id, hg['group_id'])

    hg['hit_group_content_id'] = hit_group_content_id
    hg['crawl_id'] = crawl.id
    db.insert_hit_group_status(hg)
    conn.commit()
    dbpool.putconn(conn)
