"""App configuration for the ``home`` app (HomePage + AboutPage)."""

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Landing page and about page for the site owner."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
