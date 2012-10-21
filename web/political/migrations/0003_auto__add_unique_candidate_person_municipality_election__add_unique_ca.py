# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Candidate', fields ['person', 'municipality', 'election']
        db.create_unique('political_candidate', ['person_id', 'municipality_id', 'election_id'])

        # Adding unique constraint on 'Candidate', fields ['municipality', 'number', 'election']
        db.create_unique('political_candidate', ['municipality_id', 'number', 'election_id'])

        # Adding field 'Person.index'
        db.add_column('political_person', 'index',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding unique constraint on 'Person', fields ['index', 'first_name', 'last_name', 'municipality']
        db.create_unique('political_person', ['index', 'first_name', 'last_name', 'municipality_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Person', fields ['index', 'first_name', 'last_name', 'municipality']
        db.delete_unique('political_person', ['index', 'first_name', 'last_name', 'municipality_id'])

        # Removing unique constraint on 'Candidate', fields ['municipality', 'number', 'election']
        db.delete_unique('political_candidate', ['municipality_id', 'number', 'election_id'])

        # Removing unique constraint on 'Candidate', fields ['person', 'municipality', 'election']
        db.delete_unique('political_candidate', ['person_id', 'municipality_id', 'election_id'])

        # Deleting field 'Person.index'
        db.delete_column('political_person', 'index')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'political.candidate': {
            'Meta': {'unique_together': "(('person', 'municipality', 'election'), ('number', 'municipality', 'election'))", 'object_name': 'Candidate'},
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
        'political.expense': {
            'Meta': {'unique_together': "(('candidate', 'type'),)", 'object_name': 'Expense'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.ExpenseType']"})
        },
        'political.expensehistory': {
            'Meta': {'object_name': 'ExpenseHistory'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {})
        },
        'political.expensetype': {
            'Meta': {'object_name': 'ExpenseType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
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
            'Meta': {'unique_together': "(('first_name', 'last_name', 'municipality', 'index'),)", 'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
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
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '250', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'update_error_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['political']