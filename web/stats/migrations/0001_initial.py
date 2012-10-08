# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Statistic'
        db.create_table('stats_statistic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'], null=True)),
            ('fetch_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('stats', ['Statistic'])

        # Adding unique constraint on 'Statistic', fields ['name', 'source_url']
        db.create_unique('stats_statistic', ['name', 'source_url'])

        # Adding model 'VotingPercentage'
        db.create_table('stats_votingpercentage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('statistic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Statistic'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=4)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'])),
        ))
        db.send_create_signal('stats', ['VotingPercentage'])

        # Adding model 'VotingDistrictStatistic'
        db.create_table('stats_votingdistrictstatistic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('statistic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Statistic'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=4)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'])),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.VotingDistrict'])),
        ))
        db.send_create_signal('stats', ['VotingDistrictStatistic'])

        # Adding model 'PersonElectionStatistic'
        db.create_table('stats_personelectionstatistic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('statistic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Statistic'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=4)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Person'])),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.VotingDistrict'], null=True)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
        ))
        db.send_create_signal('stats', ['PersonElectionStatistic'])


    def backwards(self, orm):
        # Removing unique constraint on 'Statistic', fields ['name', 'source_url']
        db.delete_unique('stats_statistic', ['name', 'source_url'])

        # Deleting model 'Statistic'
        db.delete_table('stats_statistic')

        # Deleting model 'VotingPercentage'
        db.delete_table('stats_votingpercentage')

        # Deleting model 'VotingDistrictStatistic'
        db.delete_table('stats_votingdistrictstatistic')

        # Deleting model 'PersonElectionStatistic'
        db.delete_table('stats_personelectionstatistic')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'political.election': {
            'Meta': {'object_name': 'Election'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'political.party': {
            'Meta': {'object_name': 'Party'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'political.person': {
            'Meta': {'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']", 'null': 'True'})
        },
        'political.votingdistrict': {
            'Meta': {'unique_together': "(('municipality', 'origin_id'),)", 'object_name': 'VotingDistrict'},
            'borders': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True'}),
            'elections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['political.Election']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'stats.personelectionstatistic': {
            'Meta': {'object_name': 'PersonElectionStatistic'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.VotingDistrict']", 'null': 'True'}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'statistic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Statistic']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '4'})
        },
        'stats.statistic': {
            'Meta': {'unique_together': "(('name', 'source_url'),)", 'object_name': 'Statistic'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']", 'null': 'True'}),
            'fetch_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'stats.votingdistrictstatistic': {
            'Meta': {'object_name': 'VotingDistrictStatistic'},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.VotingDistrict']"}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'statistic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Statistic']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '4'})
        },
        'stats.votingpercentage': {
            'Meta': {'object_name': 'VotingPercentage'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'statistic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Statistic']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '4'})
        }
    }

    complete_apps = ['stats']