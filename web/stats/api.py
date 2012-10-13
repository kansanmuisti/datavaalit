from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie.cache import SimpleCache
from tastypie import fields
from stats.models import *
from geo.models import *
from political.models import *

class StatisticResource(ModelResource):
    class Meta:
        queryset = Statistic.objects.all()
        resource_name = 'statistic'

class VotingPercentageResource(ModelResource):
    municipality = fields.ToOneField('stats.api.MunicipalityResource',
                                     'municipality')
    class Meta:
        queryset = VotingPercentage.objects.all()
        resource_name = 'voting_percentage'
        include_resource_uri = False
        excludes = ['id']

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
