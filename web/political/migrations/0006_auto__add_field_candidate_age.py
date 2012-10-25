# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Candidate.age'
        db.add_column('political_candidate', 'age',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Candidate.age'
        db.delete_column('political_candidate', 'age')


    models = {
        'geo.municipality': {
            'Meta': {'object_name': 'Municipality'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'political.campaignbudget': {
            'Meta': {'unique_together': "(('candidate', 'advance'),)", 'object_name': 'CampaignBudget'},
            'advance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Candidate']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_submitted': ('django.db.models.fields.DateTimeField', [], {})
        },
        'political.campaignexpense': {
            'Meta': {'unique_together': "(('budget', 'type'),)", 'object_name': 'CampaignExpense'},
            'budget': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.CampaignBudget']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sum': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'time_submitted': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.CampaignExpenseType']"})
        },
        'political.campaignexpensetype': {
            'Meta': {'object_name': 'CampaignExpenseType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
        },
        'political.candidate': {
            'Meta': {'unique_together': "(('person', 'municipality', 'election'), ('number', 'municipality', 'election'))", 'object_name': 'Candidate'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Election']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Municipality']", 'null': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Party']", 'null': 'True'}),
            'party_code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['political.Person']"}),
            'picture': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
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