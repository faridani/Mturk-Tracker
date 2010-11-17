# -*- coding: utf-8 -*-

import sys

try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    sys.exit('Gevent library is required: http://www.gevent.org/')


import datetime
import logging
from optparse import make_option

import gevent
from django.core.management.base import BaseCommand

from tenclouds.pid import Pid
from mturk.main.models import Crawl
from crawler import tasks


log = logging.getLogger('crawl')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--workers', dest='workers', type='int', default=5),
    )

    def handle(self, *args, **options):
        pid = Pid('mturk_crawler', True)
        self.maxworkers = options['workers']
        start_time = datetime.datetime.now()

        hits_available = tasks.hits_mainpage_total()
        groups_available = tasks.hits_groups_total()

        hits = self.fetch_hits_list()

        # create crawl object that will be filled with data later
        crawl = Crawl.objects.create(
                start_time=start_time,
                end_time=datetime.datetime.now(),
                success=True,
                hits_available=hits_available,
                hits_downloaded=0,
                groups_available=groups_available,
                groups_downloaded=len(hits))

        # TODO - manage database connections here - should be one for each
        # task working at the same time
        db = None
        jobs = []
        for hg in hits:
            jobs.append(gevent.spawn(process_group, db,  hg, crawl))
            if len(jobs) >= self.maxworkers:
                gevent.joinall(jobs)
                jobs = []
        # TODO - commit on each database connection

    def fetch_hits_list(self):
        hits = []

        counter = count(1, self.maxworkers)
        for i in counter:
            jobs = []
            for page_nr in range(i, i + self.maxworkers):
                jobs.append(gevent.spawn(tasks.hits_groups_info, page_nr))
            gevent.joinall(jobs)

            # get data from completed tasks & remove empty results
            data = [j.value for j in jobs if j.value if j.value]

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

def process_group(db, hg, crawl):
    """Gevent worker that should process single hitgroup.

    This should write some data into database and do not return any important
    data.
    """
    if db.is_hitgroup_new(hg['group_id']):
        # fresh hitgroup - create group content entry
        hg.update(tasks.hits_group_info(hg['group_id']))
        hg['fist_crawl_id'] = crawl.id
        log.info('creating new hit group content: %s', hg)
        db.insert_hit_group_content(hg)

    hg['crawl_id'] = crawl.id
    db.insert_hit_group_status(hg)
