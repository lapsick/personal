"""Create the initial page tree so a fresh site is browsable (and auditable).

Idempotent: builds the ``HomePage`` (as site root) with About, Projects,
Blog, and Contact sections plus default contact fields and ``SiteSettings`` if
they do not already exist. Useful for first-run setup and for the CI
accessibility audit, which needs live pages to crawl.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from core.models import SiteSettings


class Command(BaseCommand):
    """Seed the site with the five top-level pages and default settings."""

    help = "Create the initial home/about/projects/blog/contact page tree."

    def handle(self, *args, **options) -> None:
        """Build the page tree and default settings if not already present."""
        import datetime

        from blog.models import ArticlePage, BlogIndexPage
        from contact.models import ContactPage, FormField
        from home.models import AboutPage, HomePage
        from projects.models import ProjectIndexPage, ProjectPage

        if HomePage.objects.exists():
            self.stdout.write("HomePage already exists; nothing to seed.")
            return

        root = Page.get_first_root_node()
        site = Site.objects.get(is_default_site=True)
        # Repoint the site to the root node before deleting the default welcome
        # page, otherwise the Site row cascades away with it.
        site.root_page = root
        site.save()
        for child in root.get_children():
            child.delete()

        home = HomePage(
            title="Home",
            slug="home",
            hero_heading="Your Name — Software Engineer & Architect",
            hero_subheading="Building reliable systems on the Microsoft/.NET stack.",
            primary_cta_label="Get in touch",
            primary_cta_page=root,  # repointed to contact below
        )
        root.add_child(instance=home)

        about = AboutPage(
            title="About",
            slug="about",
            intro="<p>A short professional summary.</p>",
            body='[{"type": "paragraph", "value": "<p>Your background and expertise.</p>"}]',
        )
        home.add_child(instance=about)

        projects_index = ProjectIndexPage(title="Projects", slug="projects")
        home.add_child(instance=projects_index)
        sample_project = ProjectPage(
            title="Sample Project",
            slug="sample-project",
            summary="A short summary of a representative project.",
            problem="The problem this project addressed.",
            role="Your role and contribution.",
            approach='[{"type": "paragraph", "value": "<p>How it was solved.</p>"}]',
            outcome="The measurable result.",
            date=datetime.date.today(),
        )
        projects_index.add_child(instance=sample_project)
        sample_project.technologies.add("C#", ".NET")
        sample_project.save_revision().publish()

        blog_index = BlogIndexPage(title="Blog", slug="blog")
        home.add_child(instance=blog_index)
        blog_index.add_child(
            instance=ArticlePage(
                title="Sample Article",
                slug="sample-article",
                date=datetime.date.today(),
                summary="A short summary used in listings and social cards.",
                body='[{"type": "paragraph", "value": "<p>Article content.</p>"}]',
            )
        )

        contact = ContactPage(
            title="Contact",
            slug="contact",
            to_address="owner@example.com",
            from_address="website@example.com",
            subject="New contact form submission",
            intro="<p>Get in touch. Your message is stored only so we can reply.</p>",
            thank_you_text="<p>Thank you — your message has been sent.</p>",
        )
        home.add_child(instance=contact)
        for order, (label, ftype) in enumerate(
            [("Name", "singleline"), ("Email", "email"), ("Message", "multiline")]
        ):
            FormField.objects.create(
                page=contact, label=label, field_type=ftype, required=True, sort_order=order
            )

        home.primary_cta_page = contact
        home.save()

        site.root_page = home
        site.save()

        settings_obj = SiteSettings.load(request_or_site=site)
        settings_obj.owner_name = settings_obj.owner_name or "Your Name"
        settings_obj.professional_title = (
            settings_obj.professional_title or "Software Engineer & Architect"
        )
        settings_obj.contact_email = settings_obj.contact_email or "owner@example.com"
        settings_obj.save()

        self.stdout.write(self.style.SUCCESS("Seeded the initial site page tree."))
