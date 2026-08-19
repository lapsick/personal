"""Integration tests for home-page featured previews (US2/US3 wiring, T044)."""

import datetime

import pytest

from home.models import FeaturedArticle, FeaturedProject

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_featured_projects_and_articles_render_on_home(
    client, home_page, project_page, make_article
):
    """Selected projects and articles appear as previews on the home page (FR-007)."""
    article = make_article("Featured Article", date=datetime.date(2025, 8, 1))
    FeaturedProject.objects.create(home_page=home_page, page=project_page, sort_order=0)
    FeaturedArticle.objects.create(home_page=home_page, page=article, sort_order=0)

    assert home_page.get_featured_projects()[0].pk == project_page.pk
    assert home_page.get_featured_articles()[0].pk == article.pk

    html = client.get("/").content.decode()
    assert project_page.title in html
    assert "Featured Article" in html


def test_unpublished_featured_items_are_hidden(client, home_page, project_page):
    """Featured items that are not live are filtered out of previews."""
    FeaturedProject.objects.create(home_page=home_page, page=project_page, sort_order=0)
    project_page.unpublish()

    assert home_page.get_featured_projects() == []
