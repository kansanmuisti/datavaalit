from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.contrib.gis.resources import ModelResource as GeometryModelResource
from tastypie import fields
from geo.models import *
import json

class MunicipalityResource(ModelResource):
    def _convert_to_geojson(self, bundle):
        muni = bundle.obj
        data = {'type': 'Feature'}
        data['properties'] = bundle.data
        data['id'] = bundle.obj.pk
        borders = muni.municipalityboundary.borders
        data['geometry'] = json.loads(borders.geojson)
        bundle.data = data
        return bundle
    def alter_detail_data_to_serialize(self, request, bundle):
        if request.GET.get('format') == 'geojson':
            return self._convert_to_geojson(bundle)
        return bundle
    def alter_list_data_to_serialize(self, request, bundles):
        if request.GET.get('format') != 'geojson':
            return bundles
        data = {'type': 'FeatureCollection'}
        data['meta'] = bundles['meta']
        data['features'] = [self._convert_to_geojson(bundle) for bundle in bundles['objects']]
        return data
    def apply_filters(self, request, filters):
        obj_list = super(MunicipalityResource, self).apply_filters(request, filters)
        if request.GET.get('format') == 'geojson':
            obj_list = obj_list.select_related('municipalityboundary')
        return obj_list
    def dehydrate(self, bundle):
        alt_names = bundle.obj.municipalityname_set.all()
        for an in alt_names:
            bundle.data['name_%s' % an.language] = an.name
        return bundle
    def determine_format(self, request):
        if request.GET.get('format') == 'geojson':
            return 'application/json'
        return super(MunicipalityResource, self).determine_format(request)
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

class MunicipalityGeoJSONResource(GeometryModelResource):
    def alter_list_data_to_serialize(self, request, data):
        print data
        return data
    def dehydrate(self, bundle):
        print bundle
        return bundle
    class Meta:
        queryset = MunicipalityBoundary.objects.all().select_related('municipality')
        resource_name = 'municipality_geojson'
