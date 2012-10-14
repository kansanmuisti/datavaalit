from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from political.models import *
from geo.models import *

class ElectionResource(ModelResource):
    class Meta:
        queryset = Election.objects.all()

class PartyResource(ModelResource):
    def dehydrate(self, bundle):
        alt_names = bundle.obj.partyname_set.all()
        for an in alt_names:
            bundle.data['name_%s' % an.language] = an.name
        return bundle

    class Meta:
        queryset = Party.objects.all()
        resource_name = 'party'

class PersonResource(ModelResource):
    municipality = fields.ToOneField('geo.api.MunicipalityResource',
                                     'municipality')
    party = fields.ToOneField('political.api.PartyResource',
                              'party')
    class Meta:
        queryset = Person.objects.order_by('municipality', 'last_name', 'first_name')
        resource_name = 'person'


class CandidateResource(ModelResource):
    election = fields.ToOneField('political.api.ElectionResource', 'election')
    person = fields.ToOneField('political.api.PersonResource', 'person')
    municipality = fields.ToOneField('geo.api.MunicipalityResource',
                                     'municipality', null=True)
    party = fields.ToOneField('political.api.PartyResource', 'party')

    def dehydrate(self, bundle):
        person = bundle.obj.person
        bundle.data['person_name'] = unicode(person)
        return bundle

    class Meta:
        queryset = Candidate.objects.order_by('election', 'municipality',
                'number').select_related('person', 'election', 'municipality')
        resource_name = 'candidate'
        filtering = {
            "municipality": ('exact', 'in'),
            "election": ('exact', 'in'),
            "party": ('exact', 'in'),
        }


from social.api import FeedResource, UpdateResource
from social.models import Update
class CandidateFeedResource(FeedResource):
    candidate = fields.ToOneField('political.api.CandidateResource',
                                  'candidate', full=True)
    class Meta:
        queryset = CandidateFeed.objects.all()
        resource_name = 'candidate_social_feed'
        filtering = {
            "candidate": ALL_WITH_RELATIONS,
        }

class CandidateUpdateResource(UpdateResource):
    candidate = fields.ToOneField('political.api.CandidateResource',
                                  'feed__candidatefeed__candidate')
    class Meta:
        queryset = Update.objects.all().select_related('feed__candidatefeed__candidate')
        queryset = queryset.select_related('feed').order_by('-created_time')
        resource_name = 'candidate_social_update'
        filtering = {
            'candidate': ALL_WITH_RELATIONS,
            'feed': ALL_WITH_RELATIONS,
            'type': ALL,
            'text': ALL,
            'sub_type': ALL,
            'created_time': ALL,
            'origin_id': ('exact',),
            'interest': ALL,
        }

    def dehydrate(self, bundle):
        feed = bundle.obj.feed
        candidate = feed.candidatefeed.candidate
        bundle.data['candidate_first_name'] = candidate.person.first_name
        bundle.data['candidate_last_name'] = candidate.person.last_name
        bundle.data['candidate_party_code'] = candidate.party_code
        bundle.data['feed_picture'] = feed.picture
        bundle.data['feed_type'] = feed.type
        bundle.data['feed_origin_id'] = feed.origin_id
        return bundle


class MunicipalityCommitteeResource(ModelResource):
    municipality = fields.ToOneField('geo.api.MunicipalityResource',
                                     'municipality')
    class Meta:
        queryset = MunicipalityCommittee.objects.order_by('municipality')
        resource_name = 'municipality_committee'

class MunicipalityTrusteeResource(ModelResource):
    election = fields.ToOneField('political.api.ElectionResource', 'election')
    person = fields.ToOneField('political.api.PersonResource', 'person')
    committee = fields.ToOneField('political.api.MunicipalityCommitteeResource', 'committee')

    def dehydrate(self, bundle):
        person = bundle.obj.person
        bundle.data['person_name'] = unicode(person)
        bundle.data['person_party'] = person.party
        return bundle

    class Meta:
        queryset = MunicipalityTrustee.objects.order_by('committee', 'role')
        resource_name = 'municipality_trustee'
