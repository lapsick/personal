"""Tests for the ``seed_site`` management command (T049 support)."""

import pytest
from django.core.management import call_command
from wagtail.models import Site

from blog.models import ArticlePage, BlogIndexPage
from contact.models import ContactPage
from home.models import AboutPage, HomePage
from projects.models import ProjectIndexPage, ProjectPage

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_seed_builds_full_tree_and_sets_site_root(default_site):
    """Seeding creates all five sections and makes HomePage the site root."""
    call_command("seed_site")

    home = HomePage.objects.get()
    assert AboutPage.objects.exists()
    assert ProjectIndexPage.objects.exists()
    assert ProjectPage.objects.exists()
    assert BlogIndexPage.objects.exists()
    assert ArticlePage.objects.exists()
    assert ContactPage.objects.exists()

    site = Site.objects.get(is_default_site=True)
    assert site.root_page.pk == home.pk
    # The CTA points at the contact page.
    assert home.primary_cta_page.specific_class is ContactPage


def test_seed_is_idempotent(default_site):
    """Running the seed twice does not create duplicate pages."""
    call_command("seed_site")
    call_command("seed_site")
    assert HomePage.objects.count() == 1
