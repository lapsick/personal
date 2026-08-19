"""Integration tests for the About page and resume download (User Story 2)."""

import pytest

from core.models import SiteSettings
from core.tests.factories import DocumentFactory

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_about_shows_background_expertise_and_engagement(client, about_page):
    """About renders the summary, expertise areas, and engagement types (FR-008)."""
    html = client.get(about_page.url).content.decode()
    assert "Software engineer and architect" in html
    assert ".NET architecture" in html  # expertise area
    assert "Consulting" in html  # engagement types


def test_about_shows_resume_download_when_set(client, about_page):
    """The resume download link appears when a resume document is configured."""
    settings_obj = SiteSettings.load(request_or_site=None)
    settings_obj.resume_document = DocumentFactory()
    settings_obj.save()

    html = client.get(about_page.url).content.decode()
    assert "Download resume" in html


def test_about_without_resume_hides_link(client, about_page):
    """No resume configured means no download link (graceful)."""
    html = client.get(about_page.url).content.decode()
    assert "Download resume" not in html
