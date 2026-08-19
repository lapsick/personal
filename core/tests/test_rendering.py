"""Rendering tests: navigation, SEO head, and structural accessibility (US1).

These assert the cross-cutting HTML contract (FR-002/003, FR-022, FR-023) that
every page shares. Full axe-core/pa11y runs in CI (T049); these checks cover the
structural landmarks, labels, and ARIA wiring that gate is built on.
"""

import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_home_renders_identity_and_single_h1(client, home_page):
    """Home shows the owner's identity above the fold in exactly one ``<h1>``."""
    html = client.get("/").content.decode()
    assert html.count("<h1") == 1
    assert "Jane Doe" in html


def test_every_page_has_skip_link_and_landmarks(client, home_page):
    """Base layout provides a skip link and semantic landmarks (WCAG AA)."""
    html = client.get("/").content.decode()
    assert 'class="skip-link"' in html
    assert 'href="#main-content"' in html
    assert "<main" in html and "<header" in html and "<footer" in html
    assert 'lang="en"' in html


def test_nav_marks_current_page(client, home_page, contact_page):
    """The navigation flags the current section via ``aria-current`` (FR-003)."""
    home_html = client.get("/").content.decode()
    assert 'aria-current="page"' in home_html

    contact_html = client.get(contact_page.url).content.decode()
    # The Contact item is current on the contact route.
    assert 'aria-current="page"' in contact_html
    assert ">Contact</a>" in contact_html


def test_nav_lists_all_sections(client, home_page, contact_page):
    """Navigation renders links to the published sections (FR-002)."""
    html = client.get("/").content.decode()
    assert ">Home</a>" in html
    assert ">Contact</a>" in html


def test_seo_head_present_on_home(client, home_page):
    """Home emits title, canonical, and Open Graph metadata (FR-023)."""
    html = client.get("/").content.decode()
    assert "<title>" in html
    assert 'rel="canonical"' in html
    assert 'property="og:title"' in html
    assert 'name="twitter:card"' in html


def test_contact_form_is_accessible(client, contact_page):
    """Contact form has labelled fields, a hidden honeypot, and a privacy note."""
    html = client.get(contact_page.url).content.decode()
    # Labelled controls.
    assert "<label" in html
    # Honeypot present but hidden from assistive tech.
    assert 'aria-hidden="true"' in html
    assert "hp-field" in html
    # Privacy notice text from the intro.
    assert "reply" in html.lower()


def test_robots_txt_disallows_admin_and_links_sitemap(client, home_page):
    """robots.txt disallows admin paths and references the sitemap (FR-023)."""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Disallow: /cms/" in body
    assert "Sitemap:" in body
    assert "sitemap.xml" in body


def test_sitemap_lists_published_pages(client, home_page, contact_page):
    """The sitemap includes published pages (FR-023, SC-009)."""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    body = response.content.decode()
    assert contact_page.full_url in body or contact_page.url in body
