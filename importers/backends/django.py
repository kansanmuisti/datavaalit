from __future__ import absolute_import
import os
import sys

from importers import Backend

import pinax
import pinax.env
import pyfaceb

my_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.normpath(my_path + '/../../web')
pinax.env.setup_environ(project_path=project_path)
sys.path.append(project_path)
sys.path.append(project_path + "/apps")

from django import db
from web.stats.models import *
from web.geo.models import *
from web.political.models import *
from web.social.utils import get_facebook_graph

class DjangoBackend(Backend):
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

    def _create_or_get_person(self, info):
        args = {'first_name__iexact': info['first_name'], 'last_name__iexact': info['last_name'],
                'municipality': info['municipality']}
        try:
            person = Person.objects.get(**args)
            update_person = self.replace
        except Person.DoesNotExist:
            person = Person(first_name=info['first_name'], last_name=info['last_name'],
                            municipality=info['municipality'])
            update_person = True
        if update_person:
            if 'gender' in info:
                person.gender = info['gender']
            if 'party' in info:
                person.party = self.party_dict.get(info['party'], None)
            person.save()
        return person

    def _validate_fb_feed(self, candidate, feed_name):
        person_name = unicode(candidate.person).encode('utf8')
        feed_name = unicode(feed_name).encode('utf8')
        self.logger.debug("%s: Validating FB feed %s" % (person_name, feed_name))
        try:
            graph = get_facebook_graph(feed_name)
        except pyfaceb.exceptions.FBHTTPException as e:
            print e
            return
        if not 'category' in graph:
            self.logger.warning('%s: FB %s: not a page' % (person_name, feed_name))
            return
        origin_id = graph['id']
        if CandidateFeed.objects.filter(type='FB', origin_id=origin_id).count():
            self.logger.warning('%s: FB %s: already exists' % (person_name, feed_name))
            return

        try:
            cf = CandidateFeed.objects.get(candidate=candidate, type='FB')
            return
        except CandidateFeed.DoesNotExist:
            cf = CandidateFeed(candidate=candidate, type='FB')
        cf.origin_id = origin_id
        cf.account_name = graph.get('username', None)
        cf.save()

    def submit_candidates(self, election, candidates):
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
                self.logger.debug("saving candidates from %s" % new_muni.name)
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
                if 'party_code' in c:
                    candidate.party_code = c['party']
                candidate.save()
            if 'social' in c:
                social = c['social']
                if 'fb_feed' in social:
                    self._validate_fb_feed(candidate, social['fb_feed'])

            count += 1

        self.logger.info("%d candidates updated" % count)
        
    def submit_prebudgets(self, expenses, expense_types):
        
        # First, populate ExpenseType table if not populated already
        etypes = ExpenseType.objects.all()
        # TODO: should there be an option for adding new types? Now it's 
        # all-or-nothing. Could also be a check for provided expense types vs
        # the ones already in the database
        if not etypes:
            for expense_type in expense_types:
                etype = ExpenseType(type=expense_type['type'],
                                    description=expense_type['description'])
                etype.save()
            self.logger.debug("%s expense types added" % len(expense_types))
        else:
            self.logger.debug("No expense types to add")
                 
        # Populate the cancdidate expenses reporting table
        # TODO: for now, there is only 1 timestamp per record (i.e. candidate)
        # and thus individual expense items cannot be compared on the basis of 
        # timestamp. Items are not updated, timestamp is only used to record
        # when the report was submitted  
        
        # TODO: mathing candidates to Person objects should be done in more 
        # refined way. Expense reports have full name with potentially several
        # first names. This information should be uptadet in Person. New records
        # in Person are never created, queries will fail if person is not found.
        
        candidate_counter = 0
        candidate_updates_counter = 0
        expense_counter = 0
        missing_counter = 0
        
        for candidate_expenses in expenses:
            
            # Keep track if the candidate expenses were updated
            updated = False
            
            db.reset_queries()
            
            # Doest the candidate have any actual expenses (with numbers)
            types = [etype['type'] for etype in expense_types]
            actual_expenses = set(candidate_expenses.keys()).intersection(types)
            
            # If there are no actual expenses, continue
            if not actual_expenses:
                continue
            
            try:
                # Construct a String to describe person at hand (candidate)
                person_str = "%s %s (%s)" % (candidate_expenses['first_names'].encode('utf8') ,
                                             candidate_expenses['last_name'].encode('utf8') ,
                                             candidate_expenses['municipality'] )
                
                # Municipality given as String, do a lookup for an integer id.
                # Needed to identify the candidate
                municipality_id = Municipality.objects.get(name=candidate_expenses['municipality']).id
                
                # Since expense reports can have several firstnames, try 
                # following names as will if the 1st doesn't match. . 
                # TODO: heuristics here could be done smarter
                first_names = candidate_expenses['first_names'].split()
                
                # Break two-part names ("John-Peter") into to individual names 
                # in case one of them is the primary first name
                for first_name in first_names:
                    if '-' in first_name:
                        first_names += first_name.split('-')
                
                found = False
                
                for first_name in first_names:
                    
                    args = {'first_name__iexact': first_name, 
                            'last_name__iexact': candidate_expenses['last_name'],
                            'municipality': municipality_id}
                    
                    try:
                        # TODO: is there a more concise way of doing this?
                        person = Person.objects.get(**args)
                        candidate = Candidate.objects.get(person=person)
                        self.logger.debug("Found person %s with first name: %s." % (person_str, first_name.encode('utf-8')))
                        found = True
                        break
                    except Person.DoesNotExist:
                        self.logger.debug("Could not find person %s with first name: %s." % (person_str, first_name.encode('utf-8')))
                        continue
                    
                if not found:
                    self.logger.warning("Could not find person %s in table Person" % person_str)   
                    missing_counter += 1
                
                # What expenses (if any) has person got in the Expense table
                db_expenses = Expense.objects.filter(candidate=candidate)
                
                for actual_expense in actual_expenses:
                    # Get the id for the current expense type
                    expense = ExpenseType.objects.get(type=actual_expense)
                    
                    # Is the expense id already recorded for this person
                    expenses_in_db = [_expense.expense_type.id for _expense in db_expenses]
                    
                    if not db_expenses or expense.id not in expenses_in_db:
                        # Create a new expense item
                        sum_value = candidate_expenses[actual_expense]
                        new_expense = Expense(candidate=candidate,
                                              expense_type=expense,
                                              sum=sum_value,
                                              time_stamp=candidate_expenses['timestamp'])
                        new_expense.save()
                        msg = "New expense for %s: %s = %s" % (person_str, actual_expense, sum_value)
                        self.logger.debug(msg)
                        expense_counter += 1
                        updated = True
                        
                candidate_counter += 1
                if updated:
                    candidate_updates_counter += 1 
                
            except Municipality.DoesNotExist:
                self.logger.warning("Candidate %s: %s is not a known municipality" % (person_str,
                                                                                    candidate_expenses['municipality']))
                continue
            
            except Person.DoesNotExist:
                self.logger.warning("Person %s could not be found in table Person" % person_str)
                continue
        
        
        self.logger.info("Added %s expenses for %s candidates" % (expense_counter,
                                                                          candidate_updates_counter))
        not_updated = len(expenses) - candidate_updates_counter
        if not_updated > 0:
            self.logger.info("%s candidates not updated" % not_updated)
        if missing_counter > 0:
            self.logger.info("Could not match names for %s candidates" % missing_counter)