# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from mturk.main.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'HitGroupStatus'
        db.create_table('main_hitgroupstatus', (
            ('crawl', orm['main.HitGroupStatus:crawl']),
            ('inpage_position', orm['main.HitGroupStatus:inpage_position']),
            ('hit_group_content', orm['main.HitGroupStatus:hit_group_content']),
            ('page_number', orm['main.HitGroupStatus:page_number']),
            ('group_id', orm['main.HitGroupStatus:group_id']),
            ('hits_available', orm['main.HitGroupStatus:hits_available']),
            ('id', orm['main.HitGroupStatus:id']),
            ('hit_expiration_date', orm['main.HitGroupStatus:hit_expiration_date']),
        ))
        db.send_create_signal('main', ['HitGroupStatus'])
        
        # Adding model 'HitGroupContent'
        db.create_table('main_hitgroupcontent', (
            ('reward', orm['main.HitGroupContent:reward']),
            ('description', orm['main.HitGroupContent:description']),
            ('title', orm['main.HitGroupContent:title']),
            ('requester_name', orm['main.HitGroupContent:requester_name']),
            ('qualifications', orm['main.HitGroupContent:qualifications']),
            ('time_alloted', orm['main.HitGroupContent:time_alloted']),
            ('html', orm['main.HitGroupContent:html']),
            ('keywords', orm['main.HitGroupContent:keywords']),
            ('requester_id', orm['main.HitGroupContent:requester_id']),
            ('group_id', orm['main.HitGroupContent:group_id']),
            ('id', orm['main.HitGroupContent:id']),
        ))
        db.send_create_signal('main', ['HitGroupContent'])
        
        # Adding model 'Crawl'
        db.create_table('main_crawl', (
            ('errors', orm['main.Crawl:errors']),
            ('success', orm['main.Crawl:success']),
            ('start_time', orm['main.Crawl:start_time']),
            ('end_time', orm['main.Crawl:end_time']),
            ('groups_downloaded', orm['main.Crawl:groups_downloaded']),
            ('id', orm['main.Crawl:id']),
        ))
        db.send_create_signal('main', ['Crawl'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'HitGroupStatus'
        db.delete_table('main_hitgroupstatus')
        
        # Deleting model 'HitGroupContent'
        db.delete_table('main_hitgroupcontent')
        
        # Deleting model 'Crawl'
        db.delete_table('main_crawl')
        
    
    
    models = {
        'main.hitgroupstatus': {
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hit_expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'hit_group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inpage_position': ('django.db.models.fields.IntegerField', [], {}),
            'page_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.hitgroupcontent': {
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000000'}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'html': ('django.db.models.fields.TextField', [], {'max_length': '100000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'qualifications': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'time_alloted': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'main.crawl': {
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'errors': ('JSONField', ["'Errors'"], {'null': 'True', 'blank': 'True'}),
            'groups_downloaded': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }
    
    complete_apps = ['main']
