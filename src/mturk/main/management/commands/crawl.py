# -*- coding: utf-8 -*-

import sys

try:
    from gevent import monkey
    monkey.patch_all()
except ImportError:
    sys.exit('Gevent library is required: http://www.gevent.org/')


import os
import time
import datetime
import logging
from logging.config import fileConfig
from optparse import make_option

import gevent
from django.core.management.base import BaseCommand

from tenclouds.pid import Pid
from crawler import tasks
from crawler.db import dbpool
from mturk.main.models import Crawl, RequesterProfile


log = logging.getLogger('crawl')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--workers', dest='workers', type='int', default=3),
            make_option('--logconf', dest='logconf', metavar='FILE'),
            make_option('--debug', dest='debug', action='store_true'),
    )

    def setup_logging(self, conf_fname):
        "Basic setup for logging module"
        fileConfig(conf_fname)
        if not os.path.isfile(conf_fname):
            raise IOError('File not found: %s' % conf_fname)
        log.info('logging conf: %s', conf_fname)

    def setup_debug(self):
        from crawler.debug import debug_listen
        debug_listen()

    def handle(self, *args, **options):
        _start_time = time.time()
        pid = Pid('mturk_crawler', True)
        log.info('crawler started: %s;;%s', args, options)

        if options.get('logconf', None):
            self.setup_logging(options['logconf'])

        if options.get('debug', False):
            self.setup_debug()
            print 'Current proccess pid: %s' % pid.actual_pid
            print 'To debug, type: python -c "import os,signal; os.kill(%s, signal.SIGUSR1)"\n' % \
                    pid.actual_pid

        self.maxworkers = options['workers']
        if self.maxworkers > 9:
            # If you want to remote this limit, don't forget to change dbpool
            # object maximum number of connections. Each worker should fetch
            # 10 hitgroups and spawn single task for every one of them, that
            # will get private connection instance. So for 9 workers it's
            # already 9x10 = 90 connections required
            #
            # Also, for too many workers, amazon isn't returning valid data
            # and retrying takes much longer than using smaller amount of
            # workers
            sys.exit('Too many workers (more than 9). Quit.')
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
                groups_downloaded=groups_available)
        log.debug('fresh crawl object created: %s', crawl.id)

        # fetch those requester profiles so we could decide if their hitgroups
        # are public or not
        reqesters = RequesterProfile.objects.all_as_dict()

        # manage database connections here - should be one for each
        # task working at the same time
        groups_downloaded = 0
        total_reward = 0
        hitgroups_iter = self.hits_iter()
        for hg_pack in hitgroups_iter:
            groups_downloaded += len(hg_pack)
            jobs = []
            for hg in hg_pack:
                j = gevent.spawn(tasks.process_group, hg, crawl.id, reqesters)
                jobs.append(j)
                total_reward += hg.get('reward', 0)
            log.debug('processing pack of hitgroups objects')
            gevent.joinall(jobs, timeout=20)
            # check if all jobs ended successfully
            for job in jobs:
                if not job.ready():
                    log.error('Killing job: %s', job)
                    groups_downloaded -= 1
                    job.kill()

            if groups_downloaded >= groups_available:
                # there's no need to iterate over empty groups.. break
                break

            # amazon does not like too many requests at once, so give them a
            # quick rest...
            gevent.sleep(1)

        dbpool.closeall()

        # update crawler object
        crawl.groups_downloaded = groups_downloaded
        crawl.end_time = datetime.datetime.now()
        crawl.save()

        work_time = time.time() - _start_time
        log.info('created crawl id: %s', crawl.id)
        log.info('total reward value: %s', total_reward)
        log.info('processed hits groups downloaded: %s', groups_downloaded)
        log.info('processed hits groups available: %s', groups_available)
        log.info('work time: %.2fsec', work_time)

    def hits_iter(self):
        """Hits group lists generator.

        As long as available, return lists of parsed hits group. Because this
        method is using concurent download, number of returned elements on
        each list cannot be greater that maximum number of workers.
        """
        counter = count(1, self.maxworkers)
        for i in counter:
            jobs =[gevent.spawn(tasks.hits_groups_info, page_nr) \
                        for page_nr in range(i, i + self.maxworkers)]
            gevent.joinall(jobs)

            # get data from completed tasks & remove empty results
            hgs = []
            for job in jobs:
                if job.value:
                    hgs.extend(job.value)

            # if no data was returned, end - previous page was probably the
            # last one with results
            if not hgs:
                break

            log.debug('yielding hits group: %s', len(hgs))
            yield hgs


def count(firstval=0, step=1):
    "Port of itertools.count from python2.7"
    while True:
        yield firstval
        firstval += step
