"""URL configuration for the portfolio project.

Wires the Wagtail/Django admins, document serving, the SEO utility routes
(``/sitemap.xml`` and ``/robots.txt``), and finally hands all remaining paths
to Wagtail's page-serving mechanism (routes derive from the page tree).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from core.views import robots_txt

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    # Serve user-uploaded media locally (production is served by the platform).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    # Let Wagtail serve pages from its page tree. Keep this last.
    path("", include(wagtail_urls)),
]
