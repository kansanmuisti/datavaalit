from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie.cache import SimpleCache
from tastypie import fields
from stats.models import *

class StatisticResource(ModelResource):
    class Meta:
        queryset = Statistic.objects.all()
        resource_name = 'statistic'

class MunicipalityResource(ModelResource):
    #boundary = fields.ToOneField('stats.api.MunicipalityBoundaryResource',
    #                             attribute='municipalityboundary',
    #                             related_name='municipality',
    #                             full=True)
    def dehydrate(self, bundle):
        alt_names = bundle.obj.municipalityname_set.all()
        for an in alt_names:
            bundle.data['name_%s' % an.language] = an.name
        return bundle
    class Meta:
        queryset = Municipality.objects.all().order_by('name').select_related('municipalityboundary')
        resource_name = 'municipality'

class MunicipalityBoundaryResource(GeometryModelResource):
    class Meta:
        queryset = MunicipalityBoundary.objects.all()
        resource_name = 'municipality_boundary'
        include_resource_uri = False
        excludes = ['id']

class ElectionResource(ModelResource):
    voting_percentage = fields.ToManyField('stats.api.VotingPercentageResource',
                                           'votingpercentage_set', full=True, null=True)
    class Meta:
        queryset = Election.objects.all()

class VotingPercentageResource(ModelResource):
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    class Meta:
        queryset = VotingPercentage.objects.all()
        resource_name = 'voting_percentage'
        include_resource_uri = False
        excludes = ['id']

class CouncilMemberResource(ModelResource):
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    election = fields.ToOneField('stats.api.ElectionResource', 'election')
    class Meta:
        queryset = CouncilMember.objects.all()
        resource_name = 'council_member'

class VotingDistrictResource(GeometryModelResource):
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    elections = fields.ToManyField('stats.api.ElectionResource', 'elections')
    class Meta:
        queryset = VotingDistrict.objects.all()
        resource_name = 'voting_district'
        filtering = {
            "municipality": ('exact', 'in'),
        }

class VotingDistrictStatisticResource(ModelResource):
    election = fields.ToOneField('stats.api.ElectionResource',
                                 'election')
    district = fields.ToOneField('stats.api.VotingDistrictResource',
                                 'district')
    statistic = fields.ToOneField('stats.api.StatisticResource', 'statistic')

    def dehydrate(self, bundle):
        stat_obj = bundle.obj.statistic
        bundle.data['statistic_name'] = stat_obj.name
        return bundle

    class Meta:
        queryset = VotingDistrictStatistic.objects.all()
        resource_name = 'voting_district_statistic'
        filtering = {
            "election": ('exact', 'in'),
            "district": ALL_WITH_RELATIONS,
            "statistic": ('exact', 'in'),
        }

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
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    party = fields.ToOneField('stats.api.PartyResource',
                              'party')
    class Meta:
        queryset = Person.objects.order_by('municipality', 'last_name', 'first_name')
        resource_name = 'person'

class PersonElectionStatisticResource(ModelResource):
    election = fields.ToOneField('stats.api.ElectionResource',
                                 'election')
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    district = fields.ToOneField('stats.api.VotingDistrictResource',
                                 'district', null=True)
    person = fields.ToOneField('stats.api.PersonResource', 'person')

    def dehydrate(self, bundle):
        person = bundle.obj.person
        bundle.data['person_name'] = unicode(person)
        bundle.data['person_party'] = person.party
        return bundle

    class Meta:
        queryset = PersonElectionStatistic.objects.order_by(
                'election', 'municipality', 'district', 'person__last_name',
                'person__first_name'
        )
        resource_name = 'person_election_statistic'

class MunicipalityCommitteeResource(ModelResource):
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    class Meta:
        queryset = MunicipalityCommittee.objects.order_by('municipality')
        resource_name = 'municipality_committee'

class MunicipalityTrusteeResource(ModelResource):
    election = fields.ToOneField('stats.api.ElectionResource', 'election')
    person = fields.ToOneField('stats.api.PersonResource', 'person')
    committee = fields.ToOneField('stats.api.MunicipalityCommitteeResource', 'committee')

    def dehydrate(self, bundle):
        person = bundle.obj.person
        bundle.data['person_name'] = unicode(person)
        bundle.data['person_party'] = person.party
        return bundle

    class Meta:
        queryset = MunicipalityTrustee.objects.order_by('committee', 'role')
        resource_name = 'municipality_trustee'

class CandidateResource(ModelResource):
    election = fields.ToOneField('stats.api.ElectionResource', 'election')
    person = fields.ToOneField('stats.api.PersonResource', 'person')
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality', null=True)
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
        }

