"""Template tags for site navigation and footer rendering.

Builds the primary navigation from the Wagtail page tree so the five sections
(Home, About, Projects, Blog, Contact) render on every page (FR-002) with a
current-page indicator (FR-003).
"""

from django import template
from wagtail.models import Page, Site

from core.models import SiteSettings

register = template.Library()


def _site_root(context) -> Page | None:
    """Return the site's root page for the current request, if resolvable."""
    request = context.get("request")
    if request is None:
        return None
    site = Site.find_for_request(request)
    return site.root_page if site else None


@register.inclusion_tag("core/partials/nav.html", takes_context=True)
def main_navigation(context, calling_page: Page | None = None) -> dict:
    """Render the primary navigation.

    The menu is the site root (Home) followed by its live, public, in-menu
    children. The ``active`` flag marks the item that is the current page or an
    ancestor of it, so deep pages still highlight their section (FR-003).

    Args:
        context: The template context (provides ``request``).
        calling_page: The page currently being rendered, used to mark the
            active menu item.

    Returns:
        A context dict with ``menu_items`` and the passthrough ``request``.
    """
    root = _site_root(context)
    menu_items: list[dict] = []
    if root is not None:
        ancestor_ids = set()
        if calling_page is not None:
            ancestor_ids = set(
                calling_page.get_ancestors(inclusive=True).values_list("id", flat=True)
            )

        # Home (the root page) is always the first menu item.
        menu_items.append(
            {
                "title": "Home",
                "url": root.url,
                "active": calling_page is not None and calling_page.id == root.id,
            }
        )
        # The site's top-level pages are the fixed sections (About, Projects,
        # Blog, Contact); show every live, public one so navigation always
        # reaches all sections (FR-002).
        children = root.get_children().live().public().specific()
        for child in children:
            menu_items.append(
                {
                    "title": child.title,
                    "url": child.url,
                    "active": child.id in ancestor_ids,
                }
            )

    return {
        "menu_items": menu_items,
        "request": context.get("request"),
        "site_settings": context.get("site_settings"),
    }


@register.inclusion_tag("core/partials/footer.html", takes_context=True)
def site_footer(context) -> dict:
    """Render the site footer with owner identity and profile links.

    Returns:
        A context dict carrying the request and the ``SiteSettings`` instance
        (falling back to a lookup if the context processor did not populate it).
    """
    request = context.get("request")
    settings_obj = context.get("site_settings")
    if settings_obj is None:
        settings_obj = SiteSettings.load(request_or_site=request)
    return {"request": request, "site_settings": settings_obj}
