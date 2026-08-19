"""Utility views for the ``core`` app (robots.txt).

The XML sitemap is provided by ``wagtail.contrib.sitemaps``; this module adds
the companion ``robots.txt`` that references it and disallows admin paths
(SEO contract, FR-023).
"""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Render ``robots.txt``: allow public content, disallow admin, link sitemap.

    Args:
        request: The incoming GET request (used to build the absolute sitemap URL).

    Returns:
        A ``text/plain`` response with crawl directives.
    """
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Disallow: /cms/",
        "Disallow: /django-admin/",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
