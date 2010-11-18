# -*- coding: utf-8 -*-

import logging

from gevent import monkey
monkey.patch_all()
from gevent import socket
from gevent import thread

import psycopg2
from psycopg2 import extensions
from psycopg2.pool import ThreadedConnectionPool

from django.conf import settings



log = logging.getLogger('crawler.db')


def wait_callback(conn, timeout=None):
    while True:
        state = conn.poll()
        if state == extensions.POLL_OK:
            return
        elif state == extensions.POLL_READ:
            socket.wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            socket.wait_write(conn.fileno(), timeout=timeout)
        else:
            log.error('Psycopg2 driver error. Bad result')
            raise psycopg2.OperationalError(
                "Bad result from poll: %r" % state)

# make postgresql driver work the async way
extensions.set_wait_callback(wait_callback)


dbpool = ThreadedConnectionPool(5, 20, 'dbname=%s user=%s password=%s' % \
    (settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD))


class DB(object):
    def __init__(self, conn):
        self.tid = thread.get_ident()
        self.conn = conn
        self.curr = self.conn.cursor()

    def insert_crawl(self, data):
        """Insert crawl into database and return it's id"""
        assert self.tid == thread.get_ident()
        self.curr.execute('''
            INSERT INTO main_crawl(
                success, start_time, end_time, groups_downloaded,
                groups_available, hits_downloaded, hits_available
            ) VALUES(
                %(success)s, %(start_time)s, %(end_time)s,
                %(groups_downloaded)s, %(groups_available)s,
                %(hits_downloaded)s, %(hits_available)s
            )
        ''', data)
        # this is inside transaction, so it's quite cool
        self.curr.execute("SELECT currval('main_crawl_id_seq');")
        return self.curr.fetchone()[0]

    def hit_group_content_id(self, group_id):
        """Return hitgroup content object id related to given group or None if
        does not exists
        """
        assert self.tid == thread.get_ident()
        self.curr.execute('''
            SELECT id FROM main_hitgroupcontent WHERE group_id = %s LIMIT 1
        ''', (group_id, ))
        # if len > 0, the group already exists in database
        result = self.curr.fetchone()
        if result is None:
            return result
        return result[0]

    def insert_hit_group_content(self, data):
        assert self.tid == thread.get_ident()
        self.curr.execute('''
            INSERT INTO main_hitgroupcontent(
                reward, description, title, requester_name, qualifications,
                time_alloted, html, keywords, requester_id, group_id,
                group_id_hashed, occurrence_date, first_crawl_id
            )
            VALUES (
                %(reward)s, %(description)s, %(title)s, %(requester_name)s,
                %(qualifications)s, %(time_alloted)s, %(html)s, %(keywords)s,
                %(requester_id)s, %(group_id)s, %(group_id_hashed)s,
                %(occurrence_date)s, %(first_crawl_id)s
            )''', data)

    def insert_hit_group_status(self, data):
        assert self.tid == thread.get_ident()
        self.curr.execute('''
            INSERT INTO main_hitgroupstatus (
                crawl_id, inpage_position, hit_group_content_id, page_number,
                group_id, hits_available, hit_expiration_date
            )
            VALUES (
                %(crawl_id)s, %(inpage_position)s, %(hit_group_content_id)s,
                %(page_number)s, %(group_id)s, %(hits_available)s,
                %(hit_expiration_date)s
            )''', data)
