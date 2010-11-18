# -*- coding: utf-8 -*-

import logging

from gevent import monkey
monkey.patch_all()
from gevent import socket

import psycopg2
from psycopg2 import extensions

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


class DBPool(object):
    def __init__(self):
        self._connections = []
        self._given = []

    def get(self):
        if self._connections:
            conn = self._connections.pop()
        else:
            conn = DB()
            log.debug('creating new database connection proxy: %s', conn)
        self._given.append(conn)
        return conn

    def free(self, conn):
        self.connections.append(conn)

    def free_all_connections_given(self):
        self._connections.extend(self._given)
        self._given = []

    def commit_all(self):
        for conn in self._connections:
            conn.commit()

    def close_all(self):
        self.free_all_connections_given()
        for conn in self._connections:
            conn.rollback()
            conn.close()
        self._connections = []


class DB(object):
    def __init__(self):
        self.conn = psycopg2.connect('dbname=%s user=%s password=%s' % \
            (settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD))
        self.curr = self.conn.cursor()

    def hit_group_content_id(self, group_id):
        """Return hitgroup content object id related to given group or None if
        does not exists
        """
        self.curr.execute('''
            SELECT id FROM main_hitgroupcontent WHERE group_id = %s
        ''', (group_id, ))
        # if len > 0, the group already exists in database
        result = self.curr.fetchone()
        if result is None:
            return result
        return result[0]

    def insert_hit_group_content(self, data):
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

    def commit(self):
        self.conn.commit()
        self.curr.close()
        self.curr = self.conn.cursor()

    def close(self):
        self.curr.close()
        self.conn.close()

    def rollback(self):
        self.conn.rollback()
        self.curr.close()
        self.curr = self.conn.cursor()
