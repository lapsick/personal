"""Unit tests for the ``HomePage`` model (User Story 1)."""

import pytest
from wagtail.models import Page

from home.models import HomePage

pytestmark = pytest.mark.django_db


def test_home_page_exposes_required_hero_and_cta(home_page):
    """A published home page carries hero identity fields and a CTA target."""
    assert home_page.hero_heading
    assert home_page.hero_subheading
    assert home_page.primary_cta_label
    # The CTA points at a real, resolvable page (the contact page).
    assert isinstance(home_page.primary_cta_page.specific, Page)
    assert home_page.primary_cta_page.url is not None


def test_home_page_is_the_site_root(home_page, default_site):
    """The home page serves at the site root (``/``)."""
    default_site.refresh_from_db()
    assert default_site.root_page.pk == home_page.pk
    assert home_page.url == "/"


def test_hero_fields_are_mandatory_at_the_db_layer():
    """Hero heading/subheading are non-nullable (identity guaranteed, SC-001)."""
    assert HomePage._meta.get_field("hero_heading").blank is False
    assert HomePage._meta.get_field("hero_subheading").blank is False
    assert HomePage._meta.get_field("primary_cta_page").null is False


def test_featured_collections_default_to_empty(home_page):
    """Featured projects/articles render empty until content exists (US1 independent)."""
    assert home_page.get_featured_projects() == []
    assert home_page.get_featured_articles() == []


def test_only_one_home_page_allowed():
    """``HomePage`` is a singleton page type (max_count == 1)."""
    assert HomePage.max_count == 1
