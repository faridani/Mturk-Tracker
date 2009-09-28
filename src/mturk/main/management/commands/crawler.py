from BeautifulSoup import BeautifulSoup, ResultSet
from django.core.management.base import BaseCommand
from multiprocessing import Pipe, Process
from threading import Thread

import re
import urllib2

from crawler_callbacks import callback_allhit, callback_group
from crawler_common import get_allhit_url, get_group_url

class Command(BaseCommand):
    help = 'Runs the MTurk crawler.'
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

    def run(self):

        self.conns = []
        self.processes = []

        #max_page = int(self.get_max_page())
        max_page = 2

        interval = max_page/self.processes_count
        pages_range = self.processes_count
        if self.processes_count*(interval+1) < max_page:
            pages_range = range + 1

        pages_from = 1
        pages_to = interval if interval <= max_page else max_page

        for i in range(0, pages_range):

            parent_conn, child_conn = Pipe(False)
            self.conns.append(parent_conn)

            self.processes.append(Process(target=self.launch_worker,args=(pages_from,pages_to,child_conn,)))

            pages_from = pages_to + 1
            pages_to = pages_to + interval + 1
            if i == pages_range-2 and pages_to > max_page:
                pages_to = max_page

        print 'processes started'
        for process in self.processes: process.start()
        for process in self.processes: process.join()
        print 'processes stopped'

        for conn in self.conns:
            data = conn.recv()
            print len(data)
        #    times_processes.append(conn.recv())

        #log_results(self.log_path, generate_benchmark(times_processes))


    def get_max_page(self):
        response = urllib2.urlopen(get_allhit_url())
        html = response.read()
        pattern = re.compile(r"<a href=\".*pageNumber=([0-9]+).{150,200}Last</a>", re.MULTILINE | re.DOTALL)
        max_page = re.search(pattern, html)
        if max_page: return max_page.group(1)
        else:        return 1


    def launch_worker(self, pages_from, pages_to, conn):
        worker = Worker(callback_allhit, pages_from=pages_from, pages_to=pages_to)
        worker.start()
        worker.join()
        print 'worker finished'
        print worker.data,"\n"
        #conn.send({})
        conn.send(worker.data)
        print 'worker data sent'
        conn.close()
        print 'worker conn closed'



class Worker(Thread):

    def __init__(self, callback, **kwargs):
        Thread.__init__(self)

        self.callback = callback
        self.callback_arg = None
        self.data = {}

        if 'pages_from' in kwargs and 'pages_to' in kwargs:
            self.callback_arg = [i for i in range(kwargs['pages_from'],kwargs['pages_to']+1)]

        if 'group_id' in kwargs:
            self.callback_arg = kwargs['group_id']

    def run(self):

        self.data = self.callback(self.callback_arg)