# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Election'
        db.create_table('political_election', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('round', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('political', ['Election'])

        # Adding model 'Party'
        db.create_table('political_party', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=8)),
        ))
        db.send_create_signal('political', ['Party'])

        # Adding model 'PartyName'
        db.create_table('political_partyname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Party'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('political', ['PartyName'])

        # Adding model 'Person'
        db.create_table('political_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Party'], null=True)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
        ))
        db.send_create_signal('political', ['Person'])

        # Adding model 'Candidate'
        db.create_table('political_candidate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Person'])),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Party'], null=True)),
            ('party_code', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'])),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'], null=True)),
        ))
        db.send_create_signal('political', ['Candidate'])

        # Adding model 'VotingDistrict'
        db.create_table('political_votingdistrict', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
            ('origin_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('borders', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True)),
        ))
        db.send_create_signal('political', ['VotingDistrict'])

        # Adding unique constraint on 'VotingDistrict', fields ['municipality', 'origin_id']
        db.create_unique('political_votingdistrict', ['municipality_id', 'origin_id'])

        # Adding M2M table for field elections on 'VotingDistrict'
        db.create_table('political_votingdistrict_elections', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('votingdistrict', models.ForeignKey(orm['political.votingdistrict'], null=False)),
            ('election', models.ForeignKey(orm['political.election'], null=False))
        ))
        db.create_unique('political_votingdistrict_elections', ['votingdistrict_id', 'election_id'])

        # Adding model 'MunicipalityCommittee'
        db.create_table('political_municipalitycommittee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipality', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Municipality'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('political', ['MunicipalityCommittee'])

        # Adding model 'MunicipalityTrustee'
        db.create_table('political_municipalitytrustee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('election', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Election'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Person'])),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.MunicipalityCommittee'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('begin', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('political', ['MunicipalityTrustee'])

        # Adding model 'CandidateFeed'
        db.create_table('political_candidatefeed', (
            ('feed_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['social.Feed'], unique=True, primary_key=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['political.Candidate'])),
        ))
        db.send_create_signal('political', ['CandidateFeed'])


    def backwards(self, orm):
        # Removing unique constraint on 'VotingDistrict', fields ['municipality', 'origin_id']
        db.delete_unique('political_votingdistrict', ['municipality_id', 'origin_id'])

        # Deleting model 'Election'
        db.delete_table('political_election')

        # Deleting model 'Party'
        db.delete_table('political_party')

        # Deleting model 'PartyName'
        db.delete_table('political_partyname')

        # Deleting model 'Person'
        db.delete_table('political_person')

        # Deleting model 'Candidate'
        db.delete_table('political_candidate')

        # Deleting model 'VotingDistrict'
        db.delete_table('political_votingdistrict')

        # Removing M2M table for field elections on 'VotingDistrict'
        db.delete_table('political_votingdistrict_elections')

        # Deleting model 'MunicipalityCommittee'
        db.delete_table('political_municipalitycommittee')

        # Deleting model 'MunicipalityTrustee'
        db.delete_table('political_municipalitytrustee')

        # Deleting model 'CandidateFeed'
        db.delete_table('political_candidatefeed')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'political.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']", 'null': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']", 'null': 'True'}),
            'party_code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'political.candidatefeed': {
            'Meta': {'object_name': 'CandidateFeed', '_ormbases': ['social.Feed']},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'feed_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['social.Feed']", 'unique': 'True', 'primary_key': 'True'})
        },
        'political.election': {
            'Meta': {'object_name': 'Election'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'political.municipalitycommittee': {
            'Meta': {'object_name': 'MunicipalityCommittee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'political.municipalitytrustee': {
            'Meta': {'object_name': 'MunicipalityTrustee'},
            'begin': ('django.db.models.fields.DateField', [], {}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.MunicipalityCommittee']"}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'political.party': {
            'Meta': {'object_name': 'Party'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'political.partyname': {
            'Meta': {'object_name': 'PartyName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']"})
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
        'social.feed': {
            'Meta': {'unique_together': "(('type', 'origin_id'),)", 'object_name': 'Feed'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'origin_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_error_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['political']