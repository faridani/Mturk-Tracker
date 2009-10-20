# -*- coding: utf-8 -*-
from django.db import models
from mturk.fields import JSONField

class Crawl(models.Model):
    
    start_time          = models.DateTimeField('Start Time')
    end_time            = models.DateTimeField('End Time')
    success             = models.BooleanField('Successfoul crawl?')
    groups_downloaded   = models.IntegerField('Groups downloaded')
    errors              = JSONField('Errors', blank=True, null=True)

    def __str__(self):
        return 'Crawl: ' + str(self.start_time) + ' ' + str(self.end_time)

class HitGroupContent(models.Model):

    group_id            = models.CharField('Group ID', max_length=50, db_index=True)
    group_id_hashed     = models.BooleanField(default=False)
    requester_id        = models.CharField('Requester ID', max_length=50)
    requester_name      = models.CharField('Requester Name', max_length=500)
    reward              = models.FloatField('Reward')
    html                = models.TextField('HTML', max_length=100000000)
    description         = models.TextField('Description', max_length=1000000)
    title               = models.CharField('Title', max_length=500)
    keywords            = models.CharField('Keywords', blank=True, max_length=500, null=True)
    qualifications      = models.CharField('Qualifications', blank=True, max_length=500, null=True)
    '''
    Time in minutes
    '''
    time_alloted       = models.IntegerField('Time alloted')

    '''
    Used to recored during crawl when HitGroup is first detected
    '''
    #hit_group_status    = models.ForeignKey(HitGroupStatus)       

class HitGroupStatus(models.Model):
    
    group_id            = models.CharField('Group ID',max_length=50, db_index=True)
    hits_available      = models.IntegerField('Hits Avaliable')
    page_number         = models.IntegerField('Page Number')
    inpage_position     = models.IntegerField('In Page Position')
    hit_expiration_date = models.DateTimeField('Hit expiration Date')

    hit_group_content = models.ForeignKey(HitGroupContent)
    
    crawl               = models.ForeignKey(Crawl)

    #def __str__(self):
    #    return 'HitGroupStatus: ' + str(self.pk)
