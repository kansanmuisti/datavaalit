from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie import fields
from stats.models import *

class StatisticResource(ModelResource):
    class Meta:
        queryset = Statistic.objects.all()
        resource_name = 'statistic'

class MunicipalityResource(ModelResource):
    boundary = fields.ToOneField('stats.api.MunicipalityBoundaryResource',
                                 attribute='municipalityboundary',
                                 related_name='municipality',
                                 full=True)
    class Meta:
        queryset = Municipality.objects.all().order_by('name')
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

class VotingDistrictStatisticResource(GeometryModelResource):
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

