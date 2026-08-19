"""App configuration for the ``blog`` app (index + article pages)."""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Blog index and individual article pages."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
