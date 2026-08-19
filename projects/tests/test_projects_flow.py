"""Integration tests for the projects section routes (User Story 2)."""

import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_empty_index_renders_ok_with_empty_state(client, project_index):
    """The projects index returns 200 with an empty state when none exist (FR-011)."""
    response = client.get(project_index.url)
    assert response.status_code == 200
    assert b"No projects" in response.content


def test_index_lists_project_cards(client, project_index, project_page):
    """The index lists project cards with title, summary, and technologies."""
    html = client.get(project_index.url).content.decode()
    assert project_page.title in html
    assert project_page.summary in html
    assert "C#" in html


def test_project_detail_shows_case_study_and_safe_links(client, project_page):
    """A project detail renders the case study and safe external links (FR-010)."""
    html = client.get(project_page.url).content.decode()
    assert "Problem" in html and "Outcome" in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert "https://example.com/case" in html


def test_direct_project_entry_has_full_nav(client, project_page):
    """Entering a project URL directly still renders the site navigation."""
    html = client.get(project_page.url).content.decode()
    assert "site-nav" in html
    assert 'class="skip-link"' in html
