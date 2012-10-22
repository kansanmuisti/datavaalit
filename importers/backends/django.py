# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import re

from importers import Backend

import pinax
import pinax.env
import pyfaceb
from twython import Twython, TwythonError
from requests import ConnectionError

my_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.normpath(my_path + '/../../web')
pinax.env.setup_environ(project_path=project_path)
sys.path.append(project_path)
sys.path.append(project_path + "/apps")

from django import db
from web.stats.models import *
from web.geo.models import *
from web.political.models import *
from web.social.utils import FeedUpdater, UpdateError
from web.social.models import BrokenFeed

# Hardcoded match table to fix known problems with candidate names. 
MATCH_TABLE = {
    'Teijo Tapani Harinen (Espoo)' : {'first_name': 'Tessu Tapani'},
    'Tito Eugénio Moreira Sanches de Magalhaes (Rovaniemi)':  {'last_name': 'Moreira Sanches de Magalhães'},
    'Veikko Tapio Valkonen (Kerava)':  {'first_name': 'Veikko T'},
    'Maija-Liisa Välimäki (Turku)':  {'first_name': 'Maisa (Maija-Liisa)'},
    'Marjokaisa Piironen (Kirkkonummi)':  {'first_name': 'Kaisa'},
    'Markku Olavi Tabell (Kirkkonummi)':  {'first_name': 'Max'},
    'Simon Francisco Riestra Aedo (Tampere)':  {'first_name': 'Simón'},
    'Veli Matti Johannes Tikkaoja (Vaasa)':  {'first_name': 'Veli-Matti'},
    'Olavi Ensio Kokkonen (Jyväskylä)':  {'first_name': 'Olavi E.'},
    'Marja Leena Kukkasmäki (Pori)':  {'first_name': 'Marja-Leena'},
    'Kirsi Margit Heikkinen-Jokilahti (Savonlinna)':  {'first_name': 'Kirsi Margit'},
    'Erkki Juhani Nikulainen (Helsinki)':  {'first_name': 'Erkki (Eki)'},
    'Riitta Maria Katriina Juva (Helsinki)':  {'first_name': 'Katriina (Kati)'},
    'Silja Maria Borgarsdòttir Sandelin (Helsinki)':  {'first_name': 'Silja Borgarsdóttir'},
    'Janne Petri Hukkinen (Helsinki)':  {'first_name': 'Janne P.'},
    'Jeja Pekka Roos (Helsinki)': {'first_name': 'J.P.'},
    'Marjo Helli Anneli Huusko (Helsinki)': {'first_name': 'Marjo (Mari)'},
    'Sirkka Liisa Ikkala (Kempele)': {'first_name': 'Sirkka-Liisa'},
    'Olli Pekka Hatanpää (Vihti)': {'first_name': 'Olli Pekka'},
    'Martti Kustaa Lehto (Lahti)': {'first_name': 'Martti K.'}
}

class DjangoBackend(Backend):
    def __init__(self, *args, **kwargs):
        self.disable_twitter = False
        super(DjangoBackend, self).__init__(*args, **kwargs)

    def submit_elections(self, elections):
        count = 0
        for el in elections:
            args = {'year': el['year'], 'type': el['type']}
            if 'round' in el:
                args['round'] = el['round']

            try:
                el_obj = Election.objects.get(**args)
                if not self.replace:
                    continue
            except Election.DoesNotExist:
                el_obj = Election(**args)
            el_obj.date = el['date']
            el_obj.round = el.get('round', 1)
            count += 1
            el_obj.save()
        self.logger.info("%d elections added" % count)

    def submit_parties(self, parties):
        party_dict = {}
        for party in parties:
            if party['code'] in party_dict:
                continue
            party_dict[party['code']] = True
            try:
                obj = Party.objects.get(code=party['code'])
                if not self.replace:
                    continue
            except Party.DoesNotExist:
                obj = Party(code=party['code'])
            obj.name = party['name']
            obj.abbrev = party['abbrev']
            self.logger.debug("updating %s (%s / %s)" % (obj.code,
                obj.abbrev, obj.name))
            obj.save()
            alt_names = party.get('alt_names', [])
            for alt_name in party['alt_names']:
                args = {'party': obj, 'language': alt_name['language']}
                try:
                    pn = PartyName.objects.get(**args)
                except PartyName.DoesNotExist:
                    pn = PartyName(**args)
                pn.name = alt_name['name']
                pn.save()

    def submit_trustees(self, election, muni, trustees):
        muni = Municipality.objects.get(id=muni)
        election = Election.objects.get(**election)

        count = 0
        for t in trustees:
            args['first_name'] = t['first_name']
            args['last_name'] = t['last_name']
            args['municipality'] = muni
            person, created = Person.objects.get_or_create(**args)
            if not created:
                if person.party != args['party']:
                    self.logger.warning("Party changed for %s %s (%s -> %s)" % (person.first_name, person.last_name,
                            person.party, args['party']))
            else:
                person.party = args['party']
                person.save()

            args = {'municipality': muni, 'name': t['committee']['name']}
            assert len(args['name'])
            committee, created = MunicipalityCommittee.objects.get_or_create(**args)

            args = {'election': election, 'person': person, 'committee': committee}
            try:
                trustee = MunicipalityTrustee.objects.get(**args)
                if trustee.role != role.decode('utf8'):
                    self.logger.warning("Role changed for %s %s (%s -> %s)" %
                        (person.first_name, person.last_name, trustee.role, role.decode('utf8')))
            except MunicipalityTrustee.DoesNotExist:
                trustee = MunicipalityTrustee(**args)
                trustee.end = t['end']
                trustee.role = t['role']
                trustee.save()
                count += 1
        self.logger.info("%s: %d municipality trustee(s) saved" % count)

    def _find_person(self, info):
        if 'first_name' in info:
            first_name_str = info['first_name']
        else:
            first_name_str = info['first_names']
        person_str = "%s %s (%s)" % (first_name_str, info['last_name'],
                                     info['municipality'].name)

        # Since expense reports can have several firstnames, try
        # following names as well if the 1st doesn't match.
        # TODO: heuristics here could be done smarter
        first_names = info['first_names'].split()

        # Break two-part names ("John-Peter") into to individual names 
        # in case one of them is the primary first name
        for first_name in first_names:
            if '-' in first_name:
                first_names += first_name.split('-')

        # If it's in the match table, it needs to be in the database, too.
        # Otherwise it's a bug.
        if MATCH_TABLE.has_key(person_str.encode('utf8')):
            fix_item = MATCH_TABLE[person_str.encode('utf8')]
            person_args = {'first_name__iexact': first_names[0],
                           'last_name__iexact': info['last_name'],
                           'municipality': info['municipality']}
            for k in fix_item.keys():
                person_args['%s__iexact' % k] = fix_item[k].decode('utf8')

            self.logger.debug("Trying %s with fixed name" % person_str)
            self.logger.debug("%s" % person_args)
            return Person.objects.get(**person_args)

        # If we were given a first name, we should find an exact match.
        if 'first_name' in info:
            args = {'first_name__iexact': first_name,
                    'last_name__iexact': info['last_name'],
                    'municipality': info['municipality']}
            # For duplicate names, the importer gives us an index.
            if 'index' in info:
                args['index'] = info['index']
            try:
                person = Person.objects.get(args)
            except Person.DoesNotExist:
                return None

        for first_name in first_names:
            person_args = {'first_name__iexact': first_name, 
                           'last_name__iexact': info['last_name'],
                           'municipality': info['municipality']}
            try:
                person = Person.objects.get(**person_args)
                self.logger.debug("Found person %s with first name: %s." % (person_str, person_args['first_name__iexact']))
                return person
            except Person.DoesNotExist:
                self.logger.debug("Could not find person %s with first name: %s" % (person_str, person_args['first_name__iexact']))
            except Person.MultipleObjectsReturned:
                self.logger.error("Multiple for %s (fix index)" % person_str)

        return None

    def _create_or_get_person(self, info):
        args = {'first_name__iexact': info['first_name'], 'last_name__iexact': info['last_name'],
                'municipality': info['municipality']}
        if 'index' in info:
            args['index'] = info['index']
        else:
            args['index'] = 0
        try:
            person = Person.objects.get(**args)
            update_person = self.replace
        except Person.DoesNotExist:
            person = Person(first_name=info['first_name'], last_name=info['last_name'],
                            municipality=info['municipality'])
            if 'index' in info:
                person.index = info['index']
            update_person = True
            self.logger.info('Created person %s %s from %s' % (person.first_name, person.last_name,
                        person.municipality))
        if update_person:
            if 'gender' in info:
                person.gender = info['gender']
            if 'party' in info:
                person.party = self.party_dict.get(info['party'], None)
            if 'index' in info:
                person.index = info['index']
            else:
                person.index = 0
            person.save()
        return person

    def _validate_fb_feed(self, candidate, feed_name):
        person_name = unicode(candidate).encode('utf8')
        feed_name = unicode(feed_name).encode('utf8')
        self.logger.debug("%s: Validating FB feed %s" % (person_name, feed_name))

        # Attempt to find the feed with different parameters
        search_args = [
            {'origin_id__iexact': feed_name},
            {'account_name__iexact': feed_name}
        ]

        cf = None
        for args in search_args:
            try:
                cf = CandidateFeed.objects.get(type='FB', **args)
                self.logger.debug("%s: Feed %s found" % (person_name, feed_name))
                if cf.candidate != candidate:
                    other_name = unicode(cf.candidate.person).encode('utf8')
                    self.logger.warning("%s: Found FB feed (%s) was for %s" %
                        (person_name, feed_name, other_name))
                if not self.replace:
                    return
                break
            except CandidateFeed.DoesNotExist:
                pass

        # Check if the feed was previously marked broken.
        bf = None
        if not cf:
            try:
                bf = BrokenFeed.objects.get(type='FB', origin_id=feed_name)
                self.logger.debug("%s: FB feed %s marked broken" % (person_name, feed_name))
                if not self.replace:
                    return
            except BrokenFeed.DoesNotExist:
                pass

        # Attempt to download data from FB and mark the feed
        # as broken if we encounter trouble.
        try:
            graph = self.feed_updater.fb_graph.get(feed_name)
        except pyfaceb.exceptions.FBHTTPException as e:
            if not cf and not bf:
                bf = BrokenFeed(type='FB', origin_id=feed_name)
                bf.reason = e.message[0:49]
                bf.save()
            return
        if not 'category' in graph:
            self.logger.warning('%s: FB %s: not a page' % (person_name, feed_name))
            assert not cf
            if not bf:
                bf = BrokenFeed(type='FB', origin_id=feed_name)
                bf.reason = "not-page"
                bf.save()
            return

        # Now we know the feed is valid. If a BrokenFeed object exists,
        # remove it.
        if bf:
            bf.delete()

        origin_id = unicode(graph['id'])
        if not cf:
            try:
                cf = CandidateFeed.objects.get(type='FB', origin_id=origin_id)
                if cf.candidate != candidate:
                    self.logger.error("FB feed (id %s) was for %s, not %s" % (origin_id, cf.candidate, candidate))
                assert cf.candidate == candidate
            except CandidateFeed.DoesNotExist:
                assert CandidateFeed.objects.filter(candidate=candidate, type='FB').count() == 0
                cf = CandidateFeed(candidate=candidate, type='FB')
                self.logger.info("%s: adding FB feed %s" % (person_name, origin_id.encode('utf8')))

        cf.origin_id = origin_id
        cf.account_name = graph.get('username', None)
        cf.save()

    def _mark_broken(self, feed_type, feed_id, reason):
        self.logger.warning("Marking %s feed %s as broken (%s)" % (feed_type, feed_id, reason))
        args = {'type': feed_type, 'origin_id': feed_id}
        bf, created = BrokenFeed.objects.get_or_create(**args)
        bf.reason = reason
        bf.save()

    def _validate_twitter_feed(self, candidate, feed_name):
        person_name = unicode(candidate).encode('utf8')
        feed_name = unicode(feed_name).encode('utf8')
        self.logger.debug("%s: Validating Twitter feed %s" % (person_name, feed_name))

        twitter = self.feed_updater.twitter
        if feed_name.isdigit():
            tw_args = {'user_id': feed_name}
            orm_args = {'origin_id': feed_name}
        else:
            tw_args = {'screen_name': feed_name}
            orm_args = {'account_name__iexact': feed_name}

        try:
            cf = CandidateFeed.objects.get(type='TW', **orm_args)
            self.logger.debug("%s: Feed %s found" % (person_name, feed_name))
            if cf.candidate != candidate:
                other_name = unicode(cf.candidate.person).encode('utf8')
                self.logger.warning("%s: Found TW feed (%s) was for %s" %
                    (person_name, feed_name, other_name))
            if not self.replace:
                return
        except CandidateFeed.DoesNotExist:
            cf = None
            pass

        # Check if the feed was previously marked broken.
        bf = None
        if not cf:
            try:
                bf = BrokenFeed.objects.get(type='TW', origin_id=feed_name)
                self.logger.debug("%s: TW feed %s marked broken" % (person_name, feed_name))
                if not self.replace:
                    return
            except BrokenFeed.DoesNotExist:
                pass

        try:
            res = twitter.showUser(**tw_args)
        except TwythonError as e:
            self.logger.error('Twitter error: %s', e)
            if e.msg.startswith('Not Found:'):
                self._mark_broken("TW", feed_name, "not-found")
            elif e.msg.startswith('Bad Request:') and 'Rate limit exceeded' in e.msg:
                self.disable_twitter = True
            return
        except ConnectionError as e:
            self.logger.error('Connection error: %s', e)
            return

        origin_id = str(res['id'])
        if not cf:
            feeds = CandidateFeed.objects.filter(candidate=candidate, type='TW')
            if len(feeds):
                self.logger.warning("%s: TW feed already found (screen name '%s')" % (person_name, cf.account_name))
                return
            cf = CandidateFeed(candidate=candidate, type='TW')
            self.logger.info("%s: adding TW feed %s" % (person_name, origin_id))

        cf.origin_id = origin_id
        cf.account_name = res.get('screen_name', None)
        cf.save()

    def submit_candidates(self, election, candidates):
        if not getattr(self, 'feed_updater', None):
            self.feed_updater = FeedUpdater(self.logger)

        election = Election.objects.get(type=election['type'], year=election['year'])
        muni_dict = {}
        for muni in Municipality.objects.all():
            muni_dict[muni.pk] = muni

        self.party_dict = {}
        for party in Party.objects.all():
            self.party_dict[party.code] = party

        count = 0
        muni = None
        for c in candidates:
            db.reset_queries()
            new_muni = muni_dict[int(c['municipality']['code'])]
            if new_muni != muni:
                self.logger.info("saving candidates from %s" % new_muni.name)
            muni = new_muni
            c['municipality'] = muni

            candidate = None
            if 'number' in c:
                try:
                    candidate = Candidate.objects.get(municipality=muni, number=c['number'])
                    # FIXME: check for name mismatches here
                except Candidate.DoesNotExist:
                    # FIXME: people with same names in same municipalities
                    candidate = None
            if not candidate:
                person = self._create_or_get_person(c)
                args = {'person': person, 'election': election}
                try:
                    candidate = Candidate.objects.get(**args)
                    update_candidate = self.replace
                except Candidate.DoesNotExist:
                    candidate = Candidate(**args)
                    update_candidate = True
            else:
                person = candidate.person
                update_candidate = self.replace

            if update_candidate:
                candidate.municipality = muni
                if 'number' in c:
                    candidate.number = c['number']
                if 'profession' in c:
                    candidate.profession = c['profession']
                if 'party' in c:
                    candidate.party_code = c['party']
                    candidate.party = self.party_dict.get(c['party'], None)
                candidate.save()
            if 'social' in c:
                social = c['social']
                if 'fb_feed' in social:
                    self._validate_fb_feed(candidate, social['fb_feed'])
                if 'tw_feed' in social and not self.disable_twitter:
                    self._validate_twitter_feed(candidate, social['tw_feed'])

            count += 1

        self.logger.info("%d candidates updated" % count)

    def submit_prebudgets(self, election, expense_types, candidates):
        election = Election.objects.get(type=election['type'], year=election['year'])

        self.logger.info("Backend received %s candidates" % len(candidates))

        # First, populate ExpenseType table if not populated already
        stored_types = list(CampaignExpenseType.objects.all())
        count = 0
        for et in expense_types:
            for et_obj in stored_types:
                if et_obj.name != et['name']:
                    continue
                if not self.replace:
                    break
                et_obj.description = et['description']
                et_obj.save()
                break
            else:
                # Not found
                et_obj = CampaignExpenseType(name=et['name'],
                                             description=et['description'])
                et_obj.save()
                count += 1
        if count:
            self.logger.info("%d new expense types added" % count)
        # Replace the incoming list with the stored objects.
        expense_types = CampaignExpenseType.objects.all()

        # Populate the candidate expenses reporting table
        # TODO: for now, there is only 1 timestamp per record (i.e. candidate)
        # and thus individual expense items cannot be compared on the basis of 
        # timestamp. Items are not updated, timestamp is only used to record
        # when the report was submitted

        # TODO: mathing candidates to Person objects should be done in more 
        # refined way. Expense reports have full name with potentially several
        # first names. This information should be uptadet in Person. New records
        # in Person are never created, queries will fail if person is not found.

        candidate_counter = 0
        candidate_added_counter = 0
        candidate_updates_counter = 0
        candidate_no_expenses_counter = 0
        expense_counter = 0
        missing_counter = 0

        for cand in candidates:
            # Keep track if the candidate expenses were added
            added = False

            db.reset_queries()

            # Municipality given as String, do a lookup for an integer id.
            # Needed to identify the candidate
            try:
                muni = Municipality.objects.get(name=cand['municipality']['name'])
            except Municipality.DoesNotExist:
                print "Unable to find '%s'" % cand['municipality']['name']
            cand['municipality'] = muni

            # Construct a String to describe person at hand (candidate)
            person_str = "%s %s (%s)" % (cand['first_names'],
                                         cand['last_name'],
                                         cand['municipality'])

            person = self._find_person(cand)
            # Give up, candidate can't be found
            if not person:
                self.logger.warning("Could not find person %s in table Person" % person_str)   
                missing_counter += 1
                continue

            try:
                candidate = Candidate.objects.get(person=person,
                                                  election=election)
            except Candidate.DoesNotExist:
                self.logger.error("Could not find candidate entry for %s" % person_str)
                missing_counter += 1
                continue
            
            db_expenses = []
            
            # Get the overall prebudget
            try:
                budget = CampaignBudget.objects.get(candidate=candidate, advance=True)

                # If there is an existing budget, use that
                # What expenses (if any) has person got in the Expense table
                db_expenses = list(CampaignExpense.objects.filter(budget=budget))
            except CampaignBudget.DoesNotExist:
                # There is no previous prebudget, hence there can be no expenses
                budget = CampaignBudget(candidate=candidate, advance=True,
                                        time_submitted=cand['timestamp'])
                budget.save()
                msg = "Created a new campaign budget for %s" % person_str
                self.logger.debug(msg)

            # Is the expense list empty?
            if not cand['expenses']:
                candidate_no_expenses_counter += 1

            for exp in cand['expenses']:
                for exp_type in expense_types:
                    if exp_type.name == exp['type']:
                        break
                else:
                    raise Exception("Expense type not found. It's a bug!")

                for exp_obj in db_expenses:
                    if exp_obj.type.pk != exp_type.pk:
                        continue
                    if not self.replace:
                        break
                    exp_obj.sum = exp['value']
                    exp_obj.save()
                    msg = "Updated expense for %s: %s = %s" % (person_str, exp['type'], exp['value'])
                    
                    self.logger.debug(msg)
                    break
                else:
                    # Create a new expense item
                    new_expense = CampaignExpense(budget=budget, type=exp_type,
                                                  sum=exp['value'],
                                                  time_submitted=cand['timestamp'])
                    new_expense.save()
                    msg = "New expense for %s: %s = %s" % (person_str, exp_type.name, new_expense.sum)
                    self.logger.debug(msg)
                    expense_counter += 1
                    added = True

            if added:
                candidate_added_counter += 1
            candidate_counter += 1

        self.logger.info("Processed %d candidates" % candidate_counter)
        self.logger.info("Added %d expenses for %d candidates" % (expense_counter,
                                                                          candidate_added_counter))
        if candidate_no_expenses_counter > 0:
            self.logger.info("%s candidates have filed report but no expenses" % candidate_no_expenses_counter)
        if missing_counter > 0:
            self.logger.warning("Could not match names for %d candidates" % missing_counter)
