from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from cms.views import details as cms_page
from django.contrib import admin
admin.autodiscover()

handler500 = "pinax.views.server_error"

urlpatterns = patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^profiles/", include("idios.urls")),
    url(r"", include("cms.urls")),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
