from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from social.models import *

class FeedResource(ModelResource):
    class Meta:
        queryset = Feed.objects.all()
        resource_name = 'social_feed'

class UpdateResource(ModelResource):
    feed = fields.ToOneField('social.api.FeedResource', 'feed')
    class Meta:
        queryset = Update.objects.all()
        resource_name = 'social_update'
        filtering = {
            'feed': ALL_WITH_RELATIONS,
        }
