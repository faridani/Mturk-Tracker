'''
Copyright (c) 2009 Panagiotis G. Ipeirotis

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Initially designed and created by 10clouds.com, contact at 10clouds.com
'''
# -*- coding: utf-8 -*-
from django.db import models
from mturk.fields import JSONField
import datetime

class Crawl(models.Model):

    start_time          = models.DateTimeField('Start Time')
    end_time            = models.DateTimeField('End Time')
    hits_available      = models.IntegerField('All hits avaliable', null=True)
    hits_downloaded     = models.IntegerField('All hits downloaded', null=True)
    groups_available    = models.IntegerField('Groups available', null=True)
    groups_downloaded   = models.IntegerField('Groups downloaded', null=True)
    success             = models.BooleanField('Successfoul crawl?')
    errors              = JSONField('Errors', blank=True, null=True)
    old_id              = models.IntegerField(null=True,blank=True,unique=True,db_index=True)

    def start_day(self):
        return datetime.date(year= self.start_time.year,
                             month= self.start_time.month,
                             day= self.start_time.day)

    def __str__(self):
        return 'Crawl: ' + str(self.start_time) + ' ' + str(self.end_time)

class HitGroupContent(models.Model):
    group_id            = models.CharField('Group ID', max_length=50, db_index=True, unique=True)
    group_id_hashed     = models.BooleanField(default=False)
    requester_id        = models.CharField('Requester ID', max_length=50, db_index=True)
    requester_name      = models.CharField('Requester Name', max_length=10000)
    reward              = models.FloatField('Reward')
    html                = models.TextField('HTML', max_length=100000000)
    description         = models.TextField('Description', max_length=1000000)
    title               = models.CharField('Title', max_length=10000)
    keywords            = models.CharField('Keywords', blank=True, max_length=10000, null=True)
    qualifications      = models.CharField('Qualifications', blank=True, max_length=10000, null=True)
    occurrence_date     = models.DateTimeField('First occurrence date', blank=True, null=True, db_index=True)
    '''
    Time in minutes
    '''
    time_alloted        = models.IntegerField('Time alloted')
    first_crawl         = models.ForeignKey(Crawl, blank=True, null=True)
    is_public = models.BooleanField(default=True)


class HitGroupStatus(models.Model):
    group_id            = models.CharField('Group ID', max_length=50, db_index=True)
    hits_available      = models.IntegerField('Hits Avaliable')
    page_number         = models.IntegerField('Page Number')
    inpage_position     = models.IntegerField('In Page Position')
    hit_expiration_date = models.DateTimeField('Hit expiration Date')
    hit_group_content = models.ForeignKey(HitGroupContent)
    crawl               = models.ForeignKey(Crawl)


class DayStats(models.Model):

    date                = models.DateField('Date', db_index=True)

    arrivals_reward     = models.FloatField('Arrivals Reward')
    arrivals_hits       = models.FloatField('Arrivals Hits')
    arrivals_projects   = models.FloatField('Arrivals Projects')

    day_start_reward    = models.FloatField('Day Start Reward')
    day_start_hits     = models.FloatField('Day Start Hits')
    day_start_projects  = models.FloatField('Day Start Projects')

    day_end_reward      = models.FloatField('Day End Reward')
    day_end_hits        = models.FloatField('Day End Hits')
    day_end_projects    = models.FloatField('Day End Projects')


class CrawlAgregates(models.Model):

    reward              = models.FloatField()
    hits                = models.IntegerField()
    projects            = models.IntegerField()
    start_time          = models.DateTimeField(db_index=True)

    crawl               = models.ForeignKey(Crawl)

class HitGroupFirstOccurences(models.Model):

    requester_id        = models.CharField(max_length=50, db_index=True)
    group_id            = models.CharField(max_length=50, db_index=True)
    requester_name      = models.CharField(max_length=500)
    hits_available      = models.IntegerField()
    occurrence_date     = models.DateTimeField(db_index=True)
    reward              = models.FloatField()

    crawl               = models.ForeignKey(Crawl)
    group_status        = models.ForeignKey(HitGroupStatus)
    group_content       = models.ForeignKey(HitGroupContent)


class RequesterProfileManager(models.Manager):
    def all_as_dict(self):
        """Return all related objects as dictionary, where keys are
        `requester_id` values. Cached.
        """
        # TODO - memcache?
        data = tuple((p.requester_id, p) for p in self.all())
        # dicts are mutable, so cache tuple and generate fresh dict with every
        # call
        return dict(data)


class RequesterProfile(models.Model):
    requester_id = models.CharField(max_length=64, primary_key=True)
    is_public = models.BooleanField(default=True)

    objects = RequesterProfileManager()


class RequestersIndexQueue(models.Model):
    """List of requesters that required solr reindexing.


    Because there might be huge amount of HitGroupContent objects for single
    requester, it's impossible to index all of them during single request
    using django ORM.
    Solr is using DataImportHandler to import data directly from PostgreSQL -
    this has no timeouts.

    So, adding reference to requester in this table will force
    DataImportHandler to reindex all HitGroupContent objects related to given
    requester_id once again.

    Do not know how to delete old rows from that table using DataImportHandler
    (even if it's possible or not), so instead of cleaning that table, cration
    date token is being used to decide if RequestersIndexQueue instance is
    still valid.
    """
    requester_id = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
