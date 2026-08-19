"""App configuration for the ``contact`` app (Wagtail form page)."""

from django.apps import AppConfig


class ContactConfig(AppConfig):
    """Contact form page with honeypot + time-trap spam protection."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "contact"
