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
from crawler import tasks
from crawler.db import dbpool, DB
from mturk.main.models import Crawl


log = logging.getLogger('crawl')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--workers', dest='workers', type='int', default=3),
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

        # create crawl object that will be filled with data later
        crawl = Crawl.objects.create(
                start_time=start_time,
                end_time=datetime.datetime.now(),
                success=True,
                hits_available=hits_available,
                hits_downloaded=0,
                groups_available=groups_available,
                groups_downloaded=hits_available)
        log.debug('fresh crawl object created: %s', crawl.id)

        # manage database connections here - should be one for each
        # task working at the same time
        groups_downloaded = 0
        for hg_pack in self.hits_iter():
            groups_downloaded += len(hg_pack)
            jobs = [gevent.spawn(process_group, hg, crawl.id) for hg in hg_pack]
            log.debug('processing pack of hitgroups objects')
            gevent.joinall(jobs, timeout=15)
            # check if all jobs ended successfully
            for job in jobs:
                if not job.ready():
                    log.error('Killing job: %s', job)
                    job.kill()

        dbpool.closeall()

        # update crawler object
        crawl.groups_downloaded = groups_downloaded
        crawl.end_time = datetime.datetime.now()
        crawl.save()

        work_time = time.time() - _start_time
        log.info('processed objects: %s', groups_downloaded)
        log.info('done: %.2f', work_time)

    def hits_iter(self):
        counter = count(1, self.maxworkers)
        for i in counter:
            jobs =[gevent.spawn(tasks.hits_groups_info, page_nr) \
                        for page_nr in range(i, i + self.maxworkers)]
            gevent.joinall(jobs)

            # get data from completed tasks & remove empty results
            hits = []
            for job in jobs:
                if job.value:
                    hits.extend(job.value)

            # if no data was returned, end - previous page was probably the
            # last one with results
            if not hits:
                break
            yield hits


def count(firstval=0, step=1):
    "Port of itertools.count from python2.7"
    while True:
        yield firstval
        firstval += step

def process_group(hg, crawl_id):
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
        hg['occurrence_date'] = datetime.datetime.now()
        hg['first_crawl_id'] = crawl_id
        hg.update(tasks.hits_group_info(hg['group_id']))
        db.insert_hit_group_content(hg)
        hit_group_content_id = db.hit_group_content_id(hg['group_id'])
        log.info('new hit group content: %s;;%s',
                hit_group_content_id, hg['group_id'])

    hg['hit_group_content_id'] = hit_group_content_id
    hg['crawl_id'] = crawl_id
    db.insert_hit_group_status(hg)
    conn.commit()
    dbpool.putconn(conn)
