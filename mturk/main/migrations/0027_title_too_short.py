# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from mturk.main.models import *

class Migration:

    def forwards(self, orm):

        # Changing field 'HitGroupContent.title'
        # (to signature: django.db.models.fields.CharField(max_length=10000))
        db.alter_column('main_hitgroupcontent', 'title', orm['main.hitgroupcontent:title'])



    def backwards(self, orm):

        # Changing field 'HitGroupContent.title'
        # (to signature: django.db.models.fields.CharField(max_length=500))
        db.alter_column('main_hitgroupcontent', 'title', orm['main.hitgroupcontent:title'])



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
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'time_alloted': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '10000'})
        },
        'main.hitgroupfirstoccurences': {
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'group_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupContent']"}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'group_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HitGroupStatus']"}),
            'hits_available': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurrence_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'requester_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'requester_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'reward': ('django.db.models.fields.FloatField', [], {})
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
        },
        'main.crawlagregates': {
            'crawl': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Crawl']"}),
            'hits': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projects': ('django.db.models.fields.IntegerField', [], {}),
            'reward': ('django.db.models.fields.FloatField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        'main.crawl': {
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'errors': ('JSONField', ["'Errors'"], {'null': 'True', 'blank': 'True'}),
            'groups_downloaded': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }

    complete_apps = ['main']
