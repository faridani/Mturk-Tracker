# -*- coding: utf-8 -*-

from django.db import models, connection, transaction
from django.utils.safestring import SafeString

from mturk.fields import JSONField
import datetime


class Crawl(models.Model):

    start_time = models.DateTimeField('Start Time')
    end_time = models.DateTimeField('End Time')
    hits_available = models.IntegerField('All hits avaliable', null=True)
    hits_downloaded = models.IntegerField('All hits downloaded', null=True)
    groups_available = models.IntegerField('Groups available', null=True)
    groups_downloaded = models.IntegerField('Groups downloaded', null=True)
    success = models.BooleanField('Successfoul crawl?')
    errors = JSONField('Errors', blank=True, null=True)
    old_id = models.IntegerField(null=True, blank=True, unique=True, db_index=True)
    has_diffs = models.BooleanField("Has Diffs", db_index=True, default=False)
    is_spam_computed = models.BooleanField("Has Spam Computed", db_index=True, default=False)
    has_hits_mv = models.BooleanField("Has hits mv", db_index=True, default=False)

    def start_day(self):
        return datetime.date(year=self.start_time.year,
                             month=self.start_time.month,
                             day=self.start_time.day)

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
    is_spam = models.NullBooleanField(db_index=True)

    def prepare_for_prediction(self):

        # import csv
        # import StringIO
        import re

        num_of_qualifications = len(self.qualifications.split(',')) if self.qualifications else 0
        sanitized_html = re.sub(r'\n', ' ', self.html )
        sanitized_html = re.sub(r'\r', '', sanitized_html )

        # out = StringIO.StringIO()

        # writer = csv.writer(out)
        # writer.writerow(  )

        # csvrow = out.getvalue()
        # out.close()

        return [self.reward, self.description, self.title, self.requester_name,
            self.qualifications, num_of_qualifications, self.time_alloted,
            sanitized_html, self.keywords, "true" if self.is_public else "false"]

        # return csvrow

class HitGroupStatus(models.Model):
    group_id            = models.CharField('Group ID', max_length=50)
    hits_available      = models.IntegerField('Hits Avaliable')
    page_number         = models.IntegerField('Page Number')
    inpage_position     = models.IntegerField('In Page Position')
    hit_expiration_date = models.DateTimeField('Hit expiration Date')
    hit_group_content = models.ForeignKey(HitGroupContent)
    crawl               = models.ForeignKey(Crawl)


class DayStats(models.Model):

    date = models.DateField('Date', db_index=True)

    arrivals = models.IntegerField('Arrivals Hits', default=0)
    arrivals_value = models.FloatField('Arrivals Hits Value', default=0)
    processed = models.IntegerField('Processed Hits', default=0)
    processed_value = models.FloatField('Processed Hits Value', default=0)


class CrawlAgregates(models.Model):

    reward = models.FloatField()
    hits = models.IntegerField()
    projects = models.IntegerField()
    start_time = models.DateTimeField(db_index=True)
    spam_projects = models.IntegerField()

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


class IndexQueueManager(models.Manager):
    def add_requester(self, requester_id):
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO main_indexqueue (
                hitgroupcontent_id, requester_id, created
            )
            SELECT
                id, requester_id, now()
            FROM
                main_hitgroupcontent
            WHERE
                requester_id = %s
        ''', (requester_id, ))
        transaction.commit_unless_managed()

    def del_requester(self, requester_id):
        self.filter(requester_id=requester_id).delete()

    def del_hitgroupcontent(self, hitgroupcontent_id):
        self.filter(group_id=hitgroupcontent_id).delete()


class IndexQueue(models.Model):
    """List of ids that should be indexed in sold.

    Because we don't have to be 100% sure that given hitgroupcontent_id exists
    in HitGroupContent table, instead of using ForeignKey, simple Integer was
    used.
    """
    hitgroupcontent_id = models.IntegerField()
    requester_id = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)

    objects = IndexQueueManager()
