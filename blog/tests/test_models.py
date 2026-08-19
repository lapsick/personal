"""Unit tests for the blog page models (User Story 3)."""

import datetime

import pytest

from blog.models import ArticlePage, ArticleTag, BlogIndexPage

pytestmark = pytest.mark.django_db


def test_index_orders_articles_newest_first(blog_index, make_article):
    """The index returns articles ordered by date, most recent first (FR-012)."""
    older = make_article("Older Post", date=datetime.date(2025, 1, 1))
    newer = make_article("Newer Post", date=datetime.date(2025, 9, 1))

    articles = list(blog_index.get_articles())
    assert articles.index(newer) < articles.index(older)


def test_index_empty_state(blog_index):
    """An index with no articles yields an empty list (FR-014)."""
    assert list(blog_index.get_articles()) == []


def test_article_carries_required_fields(make_article):
    """An article exposes its date, summary, and body."""
    article = make_article("A Post", date=datetime.date(2025, 5, 5))
    assert article.date == datetime.date(2025, 5, 5)
    assert article.summary
    assert list(article.body)


def test_article_tagging(make_article):
    """Articles can be tagged via the taggit through-model."""
    article = make_article("Tagged", date=datetime.date(2025, 5, 5))
    article.tags.add("dotnet", "architecture")
    article.save()
    assert ArticleTag.objects.filter(content_object=article).count() == 2


def test_article_og_type_is_article(make_article):
    """Articles declare an ``article`` Open Graph type for social cards (FR-023)."""
    article = make_article("SEO Post", date=datetime.date(2025, 5, 5))
    assert article.og_type == "article"


def test_page_type_relationships():
    """Articles nest under the blog index; the index is a singleton."""
    assert ArticlePage.parent_page_types == ["blog.BlogIndexPage"]
    assert "blog.ArticlePage" in BlogIndexPage.subpage_types
    assert BlogIndexPage.max_count == 1
