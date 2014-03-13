# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeelingIndicator'
        db.create_table(u'thermometer_feelingindicator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'thermometer', ['FeelingIndicator'])

        # Adding model 'FeelingWord'
        db.create_table(u'thermometer_feelingword', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('word', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('untracked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'thermometer', ['FeelingWord'])

        # Adding model 'TimeFrame'
        db.create_table(u'thermometer_timeframe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('missing_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analysis_time', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('feeling_tweets', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
            ('total_tweets', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'thermometer', ['TimeFrame'])

        # Adding model 'FeelingPercent'
        db.create_table(u'thermometer_feelingpercent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('frame', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['thermometer.TimeFrame'])),
            ('feeling', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['thermometer.FeelingWord'], null=True, blank=True)),
            ('percent', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('missing_data', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('feeling_tweets', self.gf('django.db.models.fields.PositiveIntegerField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'thermometer', ['FeelingPercent'])

        # Adding index on 'FeelingPercent', fields ['missing_data', 'feeling']
        db.create_index(u'thermometer_feelingpercent', ['missing_data', 'feeling_id'])

        # Adding index on 'FeelingPercent', fields ['start_time', 'missing_data', 'feeling']
        db.create_index(u'thermometer_feelingpercent', ['start_time', 'missing_data', 'feeling_id'])


    def backwards(self, orm):
        # Removing index on 'FeelingPercent', fields ['start_time', 'missing_data', 'feeling']
        db.delete_index(u'thermometer_feelingpercent', ['start_time', 'missing_data', 'feeling_id'])

        # Removing index on 'FeelingPercent', fields ['missing_data', 'feeling']
        db.delete_index(u'thermometer_feelingpercent', ['missing_data', 'feeling_id'])

        # Deleting model 'FeelingIndicator'
        db.delete_table(u'thermometer_feelingindicator')

        # Deleting model 'FeelingWord'
        db.delete_table(u'thermometer_feelingword')

        # Deleting model 'TimeFrame'
        db.delete_table(u'thermometer_timeframe')

        # Deleting model 'FeelingPercent'
        db.delete_table(u'thermometer_feelingpercent')


    models = {
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
            'feeling_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'missing_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'total_tweets': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['thermometer']