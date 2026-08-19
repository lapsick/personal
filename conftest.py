"""Shared pytest fixtures for the whole test suite.

Provides the Wagtail page-tree roots that per-app tests build their fixtures on
(a clean root page + default site), plus a convenience fixture for building the
site's ``HomePage`` when the ``home`` app is available.
"""

import pytest
from django.core.cache import cache
from wagtail.models import Page, Site


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the cache around every test so fragment caches never leak.

    LocMemCache persists across a test session; clearing keeps query-budget and
    rendering assertions deterministic.
    """
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def root_page(db) -> Page:
    """Return the Wagtail root page (depth 1) created by the initial migration."""
    return Page.get_first_root_node()


@pytest.fixture
def default_site(db) -> Site:
    """Return the default Wagtail ``Site`` created by the initial migration."""
    return Site.objects.get(is_default_site=True)


@pytest.fixture
def home_page(root_page, default_site):
    """Build the site's ``HomePage`` (with a ``ContactPage`` child) as site root.

    Replaces Wagtail's default welcome page so ``/`` serves our ``HomePage``,
    and wires the home CTA to the contact page. Returns the ``HomePage``; the
    contact page is available at ``home_page.get_children()`` or via the
    ``contact_page`` fixture.
    """
    from contact.models import ContactPage
    from home.models import HomePage

    # Remove the default "Welcome to your new Wagtail site!" page so its slug
    # does not collide with ours and so `/` serves the HomePage.
    for child in root_page.get_children():
        child.delete()

    home = HomePage(
        title="Home",
        slug="home",
        hero_heading="Jane Doe — Software Engineer & Architect",
        hero_subheading="Building reliable systems on the Microsoft/.NET stack.",
        primary_cta_label="Get in touch",
        primary_cta_page=root_page,  # temporary; repointed to contact below
    )
    root_page.add_child(instance=home)

    contact = ContactPage(
        title="Contact",
        slug="contact",
        to_address="owner@example.com",
        from_address="website@example.com",
        subject="New contact form submission",
        intro="<p>Get in touch. We store your message only to reply.</p>",
        thank_you_text="<p>Thanks — your message has been sent.</p>",
    )
    home.add_child(instance=contact)

    home.primary_cta_page = contact
    home.save()

    default_site.root_page = home
    default_site.save()
    return home


@pytest.fixture
def about_page(home_page):
    """Return a published ``AboutPage`` child of the home page."""
    from home.models import AboutExpertise, AboutPage

    about = AboutPage(
        title="About",
        slug="about",
        intro="<p>Software engineer and architect on the Microsoft/.NET stack.</p>",
        body='[{"type": "paragraph", "value": "<p>15 years building systems.</p>"}]',
        engagement_types="<p>Consulting, fractional architecture, speaking.</p>",
    )
    home_page.add_child(instance=about)
    AboutExpertise.objects.create(about_page=about, name=".NET architecture", sort_order=0)
    AboutExpertise.objects.create(about_page=about, name="Distributed systems", sort_order=1)
    return about


@pytest.fixture
def project_index(home_page):
    """Return a published, empty ``ProjectIndexPage`` child of the home page."""
    from projects.models import ProjectIndexPage

    index = ProjectIndexPage(title="Projects", slug="projects", intro="Selected work.")
    home_page.add_child(instance=index)
    return index


@pytest.fixture
def project_page(project_index):
    """Return a published ``ProjectPage`` with links and technologies."""
    import datetime

    from projects.models import ProjectExternalLink, ProjectPage

    project = ProjectPage(
        title="Order Platform Rearchitecture",
        slug="order-platform",
        summary="Rebuilt a monolith into resilient .NET services.",
        problem="The monolith could not scale for peak load.",
        role="Lead architect and hands-on engineer.",
        approach='[{"type": "paragraph", "value": "<p>Event-driven services.</p>"}]',
        outcome="Cut p99 latency by 60%.",
        date=datetime.date(2025, 6, 1),
    )
    project_index.add_child(instance=project)
    project.technologies.add("C#", ".NET", "Azure")
    ProjectExternalLink.objects.create(
        project=project, label="Case study", url="https://example.com/case", sort_order=0
    )
    project.save_revision().publish()
    return ProjectPage.objects.get(pk=project.pk)


@pytest.fixture
def blog_index(home_page):
    """Return a published, empty ``BlogIndexPage`` child of the home page."""
    from blog.models import BlogIndexPage

    index = BlogIndexPage(title="Blog", slug="blog", intro="Notes on .NET architecture.")
    home_page.add_child(instance=index)
    return index


@pytest.fixture
def make_article(blog_index):
    """Return a factory that publishes an ``ArticlePage`` under the blog index."""
    import datetime

    from blog.models import ArticlePage

    def _make(title: str, *, date: datetime.date, slug: str | None = None) -> ArticlePage:
        article = ArticlePage(
            title=title,
            slug=slug or title.lower().replace(" ", "-"),
            date=date,
            summary=f"Summary of {title}.",
            body='[{"type": "paragraph", "value": "<p>Article body.</p>"}]',
        )
        blog_index.add_child(instance=article)
        return ArticlePage.objects.get(pk=article.pk)

    return _make


@pytest.fixture
def contact_page(home_page):
    """Return the ``ContactPage`` with default name/email/message fields added."""
    from contact.models import ContactPage, FormField

    contact = ContactPage.objects.child_of(home_page).first()
    FormField.objects.create(
        page=contact, label="Name", field_type="singleline", required=True, sort_order=0
    )
    FormField.objects.create(
        page=contact, label="Email", field_type="email", required=True, sort_order=1
    )
    FormField.objects.create(
        page=contact, label="Message", field_type="multiline", required=True, sort_order=2
    )
    return ContactPage.objects.get(pk=contact.pk)
