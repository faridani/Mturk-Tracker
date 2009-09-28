from BeautifulSoup import BeautifulSoup, ResultSet
from django.core.management.base import BaseCommand
from multiprocessing import Pipe, Process
from threading import Thread

import re
import time
import urllib2

from crawler_callbacks import callback_allhit, callback_group
from crawler_common import get_allhit_url, get_group_url

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
        if max_page: return max_page.group(1)
        else:        return 1


    def launch_worker(self, conn, callback, callback_args):
        worker = Worker(callback, callback_args)
        worker.start()
        worker.join()
        conn.send(worker.data)


    def process_values(self, values, callback):

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

            processes.append(Process(target=self.launch_worker, args=(child_conn,callback,values[values_from:values_to+1])))

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

        #max_page = int(self.get_max_page())
        max_page = 1

        self.data = self.process_values(range(1,max_page+1), callback_allhit)

        #self.process_values([result['group_id'] for result in self.data], callback_group)


class Worker(Thread):

    def __init__(self, callback, callback_args):
        Thread.__init__(self)

        self.callback = callback
        self.callback_arg = callback_args
        self.data = {}

    def run(self):

        self.data = self.callback(self.callback_arg)
