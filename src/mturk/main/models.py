from django.db import models
from mturk.fields import JSONField

class Crawl(models.Model):
    
    start_time          = models.DateTimeField('Start Time')
    end_time            = models.DateTimeField('End Time')
    success             = models.BooleanField('Successfoul crawl?')
    groups_downloaded   = models.IntegerField('Groups downloaded')
    errors              = JSONField('errrors')
    
    def __str__(self):
        return "Crawl("+ self.id + "): " + self.start_time + " to " + self.end_time

class HitGroupStatus(models.Model):
    
    group_id            = models.CharField('Group ID',max_length=50)
    hits_available      = models.IntegerField('Hits Avaliable')
    page_number         = models.IntegerField('Page Number')
    inpage_position     = models.IntegerField('In Page Position')
    hit_expiration_date = models.DateTimeField('Hit expiration Date')
    
    crawl               = models.ForeignKey(Crawl)

    def __str__(self):
        return self.id + "|" + self.mturk_group_id
    
class HitGroupContent(models.Model):
    
    group_id            = models.CharField('Group ID', max_length=50)
    requester_id        = models.CharField('Requester ID', max_length=50)
    requester_name      = models.CharField('Requester Name', max_length=500)
    reward              = models.FloatField('Reward')
    html                = models.TextField('HTML', max_length=1000000)
    description         = models.TextField('Description', max_length=1000000)
    title               = models.CharField('Title', max_length=100)
    keywords            = models.CharField('Keywords', max_length=500)
    qualifications      = models.CharField('Qualifications', max_length=500)
    '''
    Time in minutes
    '''
    time_allotted       = models.FloatField('Time alloted')
    
    '''
    Used to recored during crawl when HitGroup is first detected
    '''
    hit_group_status    = models.ForeignKey(HitGroupStatus) 