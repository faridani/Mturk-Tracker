# -*- coding: utf-8 -*-
from django.db import models
from mturk.fields import JSONField
import datetime

class Crawl(models.Model):
    
    start_time          = models.DateTimeField('Start Time')
    end_time            = models.DateTimeField('End Time')
    success             = models.BooleanField('Successfoul crawl?')
    groups_downloaded   = models.IntegerField('Groups downloaded')
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
    requester_name      = models.CharField('Requester Name', max_length=500)
    reward              = models.FloatField('Reward')
    html                = models.TextField('HTML', max_length=100000000)
    description         = models.TextField('Description', max_length=1000000)
    title               = models.CharField('Title', max_length=500)
    keywords            = models.CharField('Keywords', blank=True, max_length=500, null=True)
    qualifications      = models.CharField('Qualifications', blank=True, max_length=500, null=True)
    occurrence_date     = models.DateTimeField('First occurrence date', blank=True, null=True, db_index=True)
    '''
    Time in minutes
    '''
    time_alloted        = models.IntegerField('Time alloted')
    first_crawl         = models.ForeignKey(Crawl, blank=True, null=True)

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