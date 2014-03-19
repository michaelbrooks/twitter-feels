# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Emotion'
        db.create_table(u'fish_emotion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, blank=True)),
        ))
        db.send_create_signal(u'fish', ['Emotion'])

        # Adding model 'TimeFrame'
        db.create_table(u'fish_timeframe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('missing_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analysis_time', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('total_tweets', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'fish', ['TimeFrame'])

        # Adding model 'TimeBinCount'
        db.create_table(u'fish_timebincount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('frame', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fish.TimeFrame'])),
            ('emotion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fish.Emotion'])),
            ('bieber', self.gf('django.db.models.fields.BooleanField')()),
            ('retweet', self.gf('django.db.models.fields.BooleanField')()),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'fish', ['TimeBinCount'])

        # Adding model 'ExampleTweet'
        db.create_table(u'fish_exampletweet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frame', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fish.TimeFrame'])),
            ('tweet_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('emotion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fish.Emotion'])),
            ('bieber', self.gf('django.db.models.fields.BooleanField')()),
            ('retweet', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'fish', ['ExampleTweet'])


    def backwards(self, orm):
        # Deleting model 'Emotion'
        db.delete_table(u'fish_emotion')

        # Deleting model 'TimeFrame'
        db.delete_table(u'fish_timeframe')

        # Deleting model 'TimeBinCount'
        db.delete_table(u'fish_timebincount')

        # Deleting model 'ExampleTweet'
        db.delete_table(u'fish_exampletweet')


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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'total_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fish']