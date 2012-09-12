from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from cms.views import details as cms_page
from django.contrib import admin
from tastypie.api import Api
from stats.api import *

admin.autodiscover()

handler500 = "pinax.views.server_error"

v1_api = Api(api_name='v1')
v1_api.register(MunicipalityResource())
v1_api.register(VotingPercentageResource())
v1_api.register(ElectionResource())
v1_api.register(CouncilMemberResource())

urlpatterns = patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^profiles/", include("idios.urls")),
    url(r"^api/", include(v1_api.urls)),
    url(r"^data/municipality/$", "stats.views.municipality_border_test"),
    url(r"^data/districts/$", "stats.views.district_borders_test"),
    url(r"", include("cms.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
