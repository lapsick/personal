"""Template context processors for the ``core`` app.

Injects the owner-editable :class:`~core.models.SiteSettings` instance into every
template context as ``site_settings`` so templates can read its fields directly
(identity, contact channels, profile links).
"""

from django.http import HttpRequest

from core.models import SiteSettings


def site_settings(request: HttpRequest) -> dict:
    """Return the ``SiteSettings`` instance for the current request.

    Args:
        request: The current request (generic settings are site-independent).

    Returns:
        A context dict with the ``site_settings`` instance.
    """
    return {"site_settings": SiteSettings.load(request_or_site=request)}
