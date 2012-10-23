from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from cms.views import details as cms_page
from django.contrib import admin
from tastypie.api import Api
from stats.api import *
from geo.api import *
from political.api import *
from social.api import *

admin.autodiscover()

handler500 = "pinax.views.server_error"

v1_api = Api(api_name='v1')
# political
v1_api.register(ElectionResource())
v1_api.register(VotingDistrictResource())
v1_api.register(MunicipalityCommitteeResource())
v1_api.register(MunicipalityTrusteeResource())
v1_api.register(CandidateResource())
v1_api.register(PartyResource())
v1_api.register(PersonResource())
v1_api.register(CandidateFeedResource())
v1_api.register(CandidateUpdateResource())
# geo
v1_api.register(MunicipalityResource())
v1_api.register(MunicipalityBoundaryResource())
# social
v1_api.register(FeedResource())
v1_api.register(UpdateResource())
# stats
v1_api.register(StatisticResource())
v1_api.register(VotingPercentageResource())
v1_api.register(VotingDistrictStatisticResource())

urlpatterns = patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^profiles/", include("idios.urls")),
    url(r"^api/", include(v1_api.urls)),
    url(r"^data/candidates/$", "stats.views.explore_candidates"),
    url(r"^data/municipality/$", "stats.views.municipality_border_test"),
    url(r"^data/districts/$", "stats.views.district_borders_test"),
    url(r"^candidates/social/$", "political.views.show_candidates_social_feeds"),
    url(r"^candidates/budgets/$", "political.views.show_prebudget_stats"),
    url(r"^candidates/fetch-party-budget/$", "political.views.get_party_budget_data"),
    url(r"^candidates/change-request/$", "political.views.candidate_change_request"),
    url(r"^candidates/change-request-form/$", "political.views.candidate_change_request_form"),
    url(r"", include("cms.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
