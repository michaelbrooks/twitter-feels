# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TimeFrame.cleanup_time'
        db.add_column(u'fish_timeframe', 'cleanup_time',
                      self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TimeFrame.cleanup_time'
        db.delete_column(u'fish_timeframe', 'cleanup_time')


    models = {
        u'fish.emotion': {
            'Meta': {'object_name': 'Emotion'},
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'fish.exampletweet': {
            'Meta': {'object_name': 'ExampleTweet'},
            'bieber': ('django.db.models.fields.BooleanField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'emotion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fish.Emotion']"}),
            'frame': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fish.TimeFrame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'retweet': ('django.db.models.fields.BooleanField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'tweet_id': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'fish.timebincount': {
            'Meta': {'object_name': 'TimeBinCount'},
            'bieber': ('django.db.models.fields.BooleanField', [], {}),
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'emotion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fish.Emotion']"}),
            'frame': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fish.TimeFrame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'retweet': ('django.db.models.fields.BooleanField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'fish.timeframe': {
            'Meta': {'object_name': 'TimeFrame'},
            'analysis_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cleanup_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'total_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fish']