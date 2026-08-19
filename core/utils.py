"""Small shared helpers for the site."""

from django.db.models import Count, Max, QuerySet


def list_token(queryset: QuerySet) -> str:
    """Return a fragment-cache token that changes when a listing changes.

    Combines the row count with the most recent revision timestamp so adding,
    editing, or removing a child page invalidates any fragment keyed on it.

    Args:
        queryset: The queryset of child pages backing a listing.

    Returns:
        A short string safe to use as part of a template-fragment cache key.
    """
    agg = queryset.aggregate(count=Count("id"), latest=Max("latest_revision_created_at"))
    return f"{agg['count']}-{agg['latest']}"
