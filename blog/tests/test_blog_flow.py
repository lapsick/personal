"""Integration tests for the blog routes (User Story 3)."""

import datetime

import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_empty_index_renders_ok_with_empty_state(client, blog_index):
    """The blog index returns 200 with an empty state when no articles (FR-014)."""
    response = client.get(blog_index.url)
    assert response.status_code == 200
    assert b"No articles" in response.content


def test_index_lists_articles_newest_first(client, blog_index, make_article):
    """The index lists articles with title/date/summary, most recent first (FR-012)."""
    make_article("Older Post", date=datetime.date(2025, 1, 1))
    make_article("Newer Post", date=datetime.date(2025, 9, 1))

    html = client.get(blog_index.url).content.decode()
    assert "Older Post" in html and "Newer Post" in html
    assert html.index("Newer Post") < html.index("Older Post")


def test_direct_article_entry_renders_full_content_and_nav(client, make_article):
    """Opening an article by its own URL renders full content + nav (FR-013)."""
    article = make_article("Deep Dive", date=datetime.date(2025, 5, 5))
    html = client.get(article.url).content.decode()
    assert "Deep Dive" in html
    assert "Article body." in html
    # Self-orienting: navigation and skip link are present on direct entry.
    assert "site-nav" in html
    assert 'class="skip-link"' in html


def test_article_emits_article_og_type(client, make_article):
    """The article page emits ``og:type=article`` for correct link previews."""
    article = make_article("Shareable", date=datetime.date(2025, 5, 5))
    html = client.get(article.url).content.decode()
    assert 'property="og:type" content="article"' in html
