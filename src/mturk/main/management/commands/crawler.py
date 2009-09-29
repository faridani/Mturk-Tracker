from BeautifulSoup import BeautifulSoup, ResultSet
from django.core.management.base import BaseCommand
from django.db.models import Max
from multiprocessing import Pipe, Process
from threading import Thread

import datetime
import re
import time
import urllib2

from crawler_callbacks_data import callback_allhit, callback_details, callback_add_crawlfk
from crawler_callbacks_save import callback_database
from crawler_common import get_allhit_url, get_group_url
from mturk.main.models import Crawl

class Command(BaseCommand):
    help = 'Runs the MTurk crawler. ( This is a work in-progress. Be warned. )'
    args = '...'

    def handle(self, processes_count, **options):
        processes_count = int(processes_count)
        crawler = Crawler(processes_count)
        crawler.start()
        crawler.join()



class Crawler(Thread):

    def __init__(self, processes_count):
        Thread.__init__(self)

        self.processes_count = processes_count
        self.data = []


    def get_max_page(self):
        response = urllib2.urlopen(get_allhit_url())
        html = response.read()
        pattern = re.compile(r"<a href=\".*pageNumber=([0-9]+).{150,200}Last</a>", re.MULTILINE | re.DOTALL)
        max_page = re.search(pattern, html)
        if max_page: return int(max_page.group(1))
        else:        return 1


    def launch_worker(self, callback, callback_arg, conn=None, **kwargs):
        worker = Worker(callback, callback_arg, **kwargs)
        worker.start()
        worker.join()
        if conn:
            conn.send(worker.data)


    def process_values(self, values, callback, **kwargs):

        def receive_from_pipe(conn):
            while True:
                if conn.poll(None):
                    data = conn.recv()
                    conn.close()
                    return data
                time.sleep(1)

        data = []

        conns = []
        processes = []

        max_value = len(values)-1
        interval = max_value/self.processes_count
        values_range = self.processes_count
        if self.processes_count*(interval+1) < max_value:
            values_range = range + 1

        values_from = 0
        values_to = interval if interval <= max_value else max_value

        for i in range(0, values_range):

            parent_conn, child_conn = Pipe(False)
            conns.append(parent_conn)

            processes.append(Process(target=self.launch_worker,
                                     args=(callback,values[values_from:values_to+1],child_conn), kwargs=kwargs))

            values_from = values_to + 1
            values_to = values_to + interval + 1
            if i == values_range-2 and values_to > max_value:
                values_to = max_value

        for process in processes: process.start()

        for conn in conns:
            for result in receive_from_pipe(conn):
                data.append(result)

        for process in processes: process.join()

        return data


    def run(self):

        #self.get_max_page()

        start_time = datetime.datetime.now()

        self.data = self.process_values(range(1,3), callback_allhit)
        self.data = self.process_values(self.data, callback_details)

        crawl = Crawl(**{
            'start_time':           start_time,
            'end_time':             datetime.datetime.now(),
            'success':              True,
            'groups_downloaded':    len(self.data),
            'errors':               ''
        })
        crawl.save()

        self.data = self.process_values(self.data, callback_add_crawlfk, crawl=crawl)

        self.launch_worker(callback_database, self.data)
        

class Worker(Thread):

    def __init__(self, callback, callback_arg, **callback_kwargs):
        Thread.__init__(self)

        self.callback = callback
        self.callback_arg = callback_arg
        self.callback_kwargs = callback_kwargs
        self.data = []

    def run(self):

        self.data = self.callback(self.callback_arg, **self.callback_kwargs)
