"""Unit tests for the project page models (User Story 2)."""

import pytest
from django.core.exceptions import ValidationError

from projects.models import ProjectExternalLink, ProjectIndexPage, ProjectPage

pytestmark = pytest.mark.django_db


def test_project_index_lists_children_newest_first(project_index, project_page):
    """The index returns live child projects ordered newest-first."""
    projects = list(project_index.get_projects())
    assert project_page in projects


def test_project_index_empty_state(project_index):
    """An index with no children yields an empty project list (FR-011)."""
    assert list(project_index.get_projects()) == []


def test_project_carries_case_study_fields(project_page):
    """A project exposes the full problem/role/approach/outcome content model."""
    assert project_page.summary
    assert project_page.problem
    assert project_page.role
    assert project_page.outcome
    assert list(project_page.technologies.all())


def test_external_link_url_is_validated():
    """External-link URLs are validated (invalid input is rejected)."""
    link = ProjectExternalLink(label="Bad", url="not a url")
    with pytest.raises(ValidationError):
        link.full_clean()


def test_project_social_image_falls_back_to_featured(project_page):
    """With no explicit social image, the featured image is used for previews."""
    assert project_page.get_social_image() == project_page.featured_image


def test_page_type_relationships():
    """Projects nest under the index; the index is a singleton."""
    assert ProjectPage.parent_page_types == ["projects.ProjectIndexPage"]
    assert "projects.ProjectPage" in ProjectIndexPage.subpage_types
    assert ProjectIndexPage.max_count == 1
