# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TimeFrame.cleanup_time'
        db.add_column(u'thermometer_timeframe', 'cleanup_time',
                      self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TimeFrame.cleanup_time'
        db.delete_column(u'thermometer_timeframe', 'cleanup_time')


    models = {
        u'thermometer.exampletweet': {
            'Meta': {'object_name': 'ExampleTweet', 'index_together': "[['feeling', 'created_at']]"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'feeling': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['thermometer.FeelingWord']"}),
            'frame': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['thermometer.TimeFrame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'tweet_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'user_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'thermometer.feelingindicator': {
            'Meta': {'object_name': 'FeelingIndicator'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'thermometer.feelingpercent': {
            'Meta': {'object_name': 'FeelingPercent', 'index_together': "[['missing_data', 'feeling'], ['start_time', 'missing_data', 'feeling']]"},
            'feeling': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['thermometer.FeelingWord']", 'null': 'True', 'blank': 'True'}),
            'feeling_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'frame': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['thermometer.TimeFrame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'thermometer.feelingword': {
            'Meta': {'object_name': 'FeelingWord'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'untracked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'thermometer.timeframe': {
            'Meta': {'object_name': 'TimeFrame'},
            'analysis_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cleanup_time': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'feeling_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'total_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['thermometer']