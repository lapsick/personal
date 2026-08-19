"""App configuration for the ``core`` app (shared building blocks)."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Shared mixins, StreamField blocks, site settings, and base templates."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
