from tastypie.resources import ModelResource
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie import fields
from stats.models import *

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
    election = fields.ToOneField('stats.api.ElectionResource', 'election')
    class Meta:
        queryset = VotingDistrict.objects.all()
        resource_name = 'voting_district'
