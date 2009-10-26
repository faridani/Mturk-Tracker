# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from mturk.main.models import *

class Migration:
    
    def forwards(self, orm):
        
        db.execute("drop view hits_v")
        db.execute("""
            SELECT drop_matview('hits_mv');
        """)        
        
        db.execute("""
        CREATE VIEW hits_v AS 
            select 
                p.id as "status_id", 
                q.id as "content_id", 
                p.group_id, 
                p.crawl_id, 
                q.requester_id, 
                p.hits_available, 
                p.page_number, 
                p.inpage_position, 
                p.hit_expiration_date, 
                q.reward, 
                q.time_alloted 
            from main_hitgroupstatus p left join main_hitgroupcontent q on (p.group_id = q.group_id)""")
        
        db.execute("""
            SELECT create_matview('hits_mv', 'hits_v');
        """)        
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'main.hitgroupstatus': {
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'hit_expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'hit_group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inpage_position': ('django.db.models.fields.IntegerField', [], {}),
            'page_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.hitgroupcontent': {
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000000'}),
            'first_crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']", 'null': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'group_id_hashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'max_length': '100000000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'occurrence_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'qualifications': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
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
        },
        'main.daystats': {
            'arrivals_hits': ('django.db.models.fields.FloatField', [], {}),
            'arrivals_projects': ('django.db.models.fields.FloatField', [], {}),
            'arrivals_reward': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'day_end_hits': ('django.db.models.fields.FloatField', [], {}),
            'day_end_projects': ('django.db.models.fields.FloatField', [], {}),
            'day_end_reward': ('django.db.models.fields.FloatField', [], {}),
            'day_start_hits': ('django.db.models.fields.FloatField', [], {}),
            'day_start_projects': ('django.db.models.fields.FloatField', [], {}),
            'day_start_reward': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['main']
