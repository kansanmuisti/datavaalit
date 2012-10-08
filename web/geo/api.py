from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie import fields
from geo.models import *

class MunicipalityResource(ModelResource):
    def dehydrate(self, bundle):
        alt_names = bundle.obj.municipalityname_set.all()
        for an in alt_names:
            bundle.data['name_%s' % an.language] = an.name
        return bundle
    class Meta:
        queryset = Municipality.objects.all().order_by('name').select_related('municipalityboundary')
        resource_name = 'municipality'

class MunicipalityBoundaryResource(GeometryModelResource):
    municipality = fields.ToOneField('geo.api.MunicipalityResource', 'municipality')
    class Meta:
        queryset = MunicipalityBoundary.objects.all()
        resource_name = 'municipality_boundary'
        filtering = {
            'municipality': ALL
        }
