"""Sitemap & robots coverage across all page types (T046, FR-023, SC-009)."""

import datetime

import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_sitemap_includes_all_page_types_and_articles(
    client, home_page, about_page, project_page, blog_index, make_article, contact_page
):
    """Every published page type and article appears in the sitemap (SC-009)."""
    article = make_article("Indexed Article", date=datetime.date(2025, 7, 1))

    body = client.get("/sitemap.xml").content.decode()

    for page in (home_page, about_page, project_page, blog_index, contact_page, article):
        assert page.full_url in body, f"{page.title} missing from sitemap"
    # The projects index is the parent of project_page and must be listed too.
    assert project_page.get_parent().specific.full_url in body


def test_sitemap_excludes_admin(client, home_page):
    """Admin URLs are never listed in the sitemap."""
    body = client.get("/sitemap.xml").content.decode()
    assert "/cms/" not in body
    assert "/django-admin/" not in body


def test_robots_disallows_admin_and_references_sitemap(client, home_page):
    """robots.txt disallows admin paths and points at the sitemap (FR-023)."""
    body = client.get("/robots.txt").content.decode()
    assert "Disallow: /cms/" in body
    assert "Disallow: /django-admin/" in body
    assert "/sitemap.xml" in body


def test_draft_pages_are_excluded_from_sitemap(client, blog_index, make_article):
    """Unpublished (draft) articles do not appear in the sitemap."""
    article = make_article("Draft Article", date=datetime.date(2025, 7, 1))
    article.unpublish()

    body = client.get("/sitemap.xml").content.decode()
    assert article.full_url not in body
