# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from mturk.main.models import *
from django.conf import settings
import os


class Migration:
    '''
    Materialised views according to http://tech.jonathangardner.net/wiki/PostgreSQL/Materialized_Views
    '''
    def forwards(self, orm):

        mviews_sql = os.path.join(settings.ROOT_PATH, 'mturk/main/migrations/mviews.sql')
        db.execute_many(open(mviews_sql).read())

    def backwards(self, orm):
        mviews_drop_sql = os.path.join(settings.ROOT_PATH, 'mturk/main/migrations/mviews_drop.sql')
        db.execute_many(open(mviews_drop_sql).read())

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
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
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
