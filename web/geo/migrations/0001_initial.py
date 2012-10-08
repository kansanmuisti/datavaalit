# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Municipality'
        db.create_table('geo_municipality', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('geo', ['Municipality'])

        # Adding model 'MunicipalityName'
        db.create_table('geo_municipalityname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('geo', ['MunicipalityName'])

        # Adding model 'MunicipalityBoundary'
        db.create_table('geo_municipalityboundary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['geo.Municipality'], unique=True)),
            ('borders', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('geo', ['MunicipalityBoundary'])


    def backwards(self, orm):
        # Deleting model 'Municipality'
        db.delete_table('geo_municipality')

        # Deleting model 'MunicipalityName'
        db.delete_table('geo_municipalityname')

        # Deleting model 'MunicipalityBoundary'
        db.delete_table('geo_municipalityboundary')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'geo.municipalityboundary': {
            'Meta': {'object_name': 'MunicipalityBoundary'},
            'borders': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['geo.Municipality']", 'unique': 'True'})
        },
        'geo.municipalityname': {
            'Meta': {'object_name': 'MunicipalityName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['geo']