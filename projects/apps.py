"""App configuration for the ``projects`` app (index + project pages)."""

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Project index and individual project detail pages."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"
