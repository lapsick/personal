"""Performance tests: the projects index must not issue N+1 queries (T047)."""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from projects.models import ProjectPage

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _add_project(index, n: int) -> None:
    project = ProjectPage(
        title=f"Project {n}",
        slug=f"project-{n}",
        summary="Summary.",
        problem="Problem.",
        role="Role.",
        approach='[{"type": "paragraph", "value": "<p>Approach.</p>"}]',
        outcome="Outcome.",
        date=datetime.date(2025, 1, 1) + datetime.timedelta(days=n),
    )
    index.add_child(instance=project)
    project.technologies.add("C#", ".NET", f"Tag{n}")
    project.save_revision().publish()


def test_projects_index_query_count_is_flat(client, project_index):
    """Rendering the index costs a constant number of queries regardless of size."""
    for i in range(2):
        _add_project(project_index, i)
    with CaptureQueriesContext(connection) as ctx_small:
        client.get(project_index.url)
    small = len(ctx_small)

    for i in range(2, 8):
        _add_project(project_index, i)
    with CaptureQueriesContext(connection) as ctx_large:
        client.get(project_index.url)
    large = len(ctx_large)

    # 2 projects vs 8 projects: query count must not grow proportionally.
    # Allow a tiny constant slack for prefetch batching, never per-item growth.
    assert large - small <= 2, f"possible N+1: {small} -> {large} queries"
