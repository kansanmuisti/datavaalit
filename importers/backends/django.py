from __future__ import absolute_import
import os
import sys

from importers import Backend

import pinax
import pinax.env

my_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.normpath(my_path + '/../../web')
pinax.env.setup_environ(project_path=project_path)
sys.path.append(project_path)
sys.path.append(project_path + "/apps")

from django import db
from web.stats.models import *

class DjangoBackend(Backend):
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
                    pn = PartyName(args)
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

    def submit_candidates(self, election, candidates):
        election = Election.objects.get(type=election['type'], year=election['year'])
        muni_dict = {}
        for muni in Municipality.objects.all():
            muni_dict[muni.pk] = muni
        party_dict = {}
        for party in Party.objects.all():
            party_dict[party.code] = party

        count = 0
        muni = None
        for c in candidates:
            db.reset_queries()
            new_muni = muni_dict[int(c['municipality']['code'])]
            if new_muni != muni:
                self.logger.debug("saving candidates from %s" % new_muni.name)
            muni = new_muni
            args = {'first_name': c['first_name'], 'last_name': c['last_name'],
                    'municipality': muni}
            try:
                person = Person.objects.get(**args)
                update_person = self.replace
            except Person.DoesNotExist:
                person = Person(**args)
                update_person = True
            if update_person:
                person.gender = c['gender']
                person.party = party_dict.get(c['party'], None)
                person.save()

            args = {'person': person, 'election': election}
            try:
                candidate = Candidate.objects.get(**args)
                if not self.replace:
                    continue
            except Candidate.DoesNotExist:
                candidate = Candidate(**args)
            candidate.municipality = muni
            candidate.number = c['number']
            candidate.profession = c['profession']
            candidate.party_code = c['party']
            candidate.save()

            count += 1
        self.logger.info("%d candidates updated" % count)
