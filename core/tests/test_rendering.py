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


def test_base_loads_pico_before_main_css(client, home_page):
    """Pico is linked before the project override layer (feature 002, contract C1).

    The override layer must win where it intentionally overrides Pico, so the
    vendored framework MUST appear earlier in the document than ``main.css``.
    """
    html = client.get("/").content.decode()
    assert "css/vendor/pico.min.css" in html
    assert "css/main.css" in html
    assert html.index("css/vendor/pico.min.css") < html.index("css/main.css")
    # Dual light/dark scheme is declared so native controls theme correctly.
    assert 'name="color-scheme"' in html
    assert "light dark" in html


def test_all_body_blocks_render(client, blog_index):
    """Every StreamField block type renders without error (feature 002, SC-002).

    A single article carrying heading, paragraph, code, image, and quote blocks
    must render 200 with each block's wrapper present — proof that no block falls
    back to unstyled/broken output under the Pico restyle.
    """
    import datetime
    import json

    from blog.models import ArticlePage
    from core.tests.factories import ImageFactory

    image = ImageFactory()
    body = json.dumps(
        [
            {"type": "heading", "value": {"text": "A section heading", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Body <strong>text</strong> here.</p>"},
            {"type": "code", "value": {"language": "python", "code": "x = 1"}},
            {
                "type": "image",
                "value": {"image": image.pk, "alt_text": "Alt text", "caption": "A caption"},
            },
            {"type": "quote", "value": {"quote": "A memorable quote.", "attribution": "Someone"}},
        ]
    )
    article = ArticlePage(
        title="All Blocks",
        slug="all-blocks",
        date=datetime.date(2025, 1, 1),
        summary="Exercises every body block.",
        body=body,
    )
    blog_index.add_child(instance=article)
    article = ArticlePage.objects.get(pk=article.pk)

    response = client.get(article.url)
    assert response.status_code == 200
    html = response.content.decode()
    assert "body-heading" in html and "A section heading" in html
    assert "body-richtext" in html
    assert "body-code" in html and "python" in html
    assert "body-image" in html and "A caption" in html
    assert "body-quote" in html and "A memorable quote." in html


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
