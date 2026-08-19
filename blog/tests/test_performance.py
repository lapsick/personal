"""Performance tests: the blog index must not issue N+1 queries (T047)."""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_blog_index_query_count_is_flat(client, blog_index, make_article):
    """Rendering the blog index costs a constant number of queries as it grows."""
    for i in range(2):
        make_article(f"Post {i}", date=datetime.date(2025, 1, 1) + datetime.timedelta(days=i))
    with CaptureQueriesContext(connection) as ctx_small:
        client.get(blog_index.url)
    small = len(ctx_small)

    for i in range(2, 8):
        make_article(f"Post {i}", date=datetime.date(2025, 1, 1) + datetime.timedelta(days=i))
    with CaptureQueriesContext(connection) as ctx_large:
        client.get(blog_index.url)
    large = len(ctx_large)

    assert large - small <= 2, f"possible N+1: {small} -> {large} queries"
