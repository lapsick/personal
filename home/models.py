"""Page models for the landing page (``HomePage``) and about page.

``AboutPage`` is added in User Story 2; this module currently holds the
``HomePage`` and its optional featured-content relations, which render empty
until projects/articles exist (keeping User Story 1 independently testable).
"""

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from core.blocks import body_blocks
from core.models import BasePage


class HomePage(BasePage):
    """The site landing page: identity above the fold + one-click contact CTA.

    Hero fields and the CTA target are required so the "identity within seconds
    and one-click contact" outcome (SC-001, SC-002) is structurally guaranteed.
    """

    hero_heading = models.CharField(
        max_length=150,
        help_text="Owner name + title, shown above the fold (FR-005).",
    )
    hero_subheading = models.CharField(
        max_length=255,
        help_text="Specialization statement (e.g. Microsoft/.NET focus).",
    )
    primary_cta_label = models.CharField(
        max_length=60,
        default="Get in touch",
        help_text='Call-to-action label, e.g. "Get in touch" (FR-006).',
    )
    primary_cta_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.PROTECT,
        related_name="+",
        help_text="Target of the primary CTA (typically the contact page).",
    )
    intro = StreamField(
        body_blocks(),
        blank=True,
        help_text="Optional short value proposition below the hero.",
    )

    content_panels = [
        *BasePage.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("hero_heading"),
                FieldPanel("hero_subheading"),
                FieldPanel("primary_cta_label"),
                PageChooserPanel("primary_cta_page"),
            ],
            heading="Hero",
        ),
        FieldPanel("intro"),
        InlinePanel("featured_projects", label="Featured projects", max_num=6),
        InlinePanel("featured_articles", label="Featured articles", max_num=6),
    ]

    # Only one HomePage, living at the site root.
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    def get_featured_projects(self) -> list:
        """Return the specific, live, public featured project pages, in order."""
        return [
            fp.page.specific
            for fp in self.featured_projects.select_related("page").all()
            if fp.page and fp.page.live
        ]

    def get_featured_articles(self) -> list:
        """Return the specific, live, public featured article pages, in order."""
        return [
            fa.page.specific
            for fa in self.featured_articles.select_related("page").all()
            if fa.page and fa.page.live
        ]


class AboutPage(BasePage):
    """The owner's background and expertise, with a resume download (FR-008).

    The resume itself lives on ``SiteSettings.resume_document`` so it stays
    owner-maintainable; this page surfaces the download link when one is set.
    """

    intro = RichTextField(help_text="Professional summary shown at the top.")
    body = StreamField(
        body_blocks(),
        help_text="Background and expertise (esp. .NET architecture).",
    )
    engagement_types = RichTextField(
        blank=True,
        help_text="What engagements the owner is open to.",
    )

    content_panels = [
        *BasePage.content_panels,
        FieldPanel("intro"),
        FieldPanel("body"),
        InlinePanel("expertise_areas", label="Expertise areas"),
        FieldPanel("engagement_types"),
    ]

    max_count = 1

    def get_expertise(self) -> list[str]:
        """Return the ordered list of expertise-area labels."""
        return [area.name for area in self.expertise_areas.all()]


class AboutExpertise(Orderable):
    """A single expertise/skill area listed on the about page."""

    about_page = ParentalKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name="expertise_areas",
    )
    name = models.CharField(max_length=100)

    panels = [FieldPanel("name")]


class FeaturedProject(Orderable):
    """An ordered reference from the home page to a project page (trust signal).

    Targets a generic ``Page`` so the ``home`` app stays independent of the
    ``projects`` app; the owner selects project pages here and the home
    template renders them as cards.
    """

    home_page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="featured_projects")
    page = models.ForeignKey("wagtailcore.Page", on_delete=models.CASCADE, related_name="+")

    panels = [PageChooserPanel("page")]


class FeaturedArticle(Orderable):
    """An ordered reference from the home page to an article page.

    Targets a generic ``Page`` so the ``home`` app stays independent of the
    ``blog`` app; the owner selects article pages here.
    """

    home_page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name="featured_articles")
    page = models.ForeignKey("wagtailcore.Page", on_delete=models.CASCADE, related_name="+")

    panels = [PageChooserPanel("page")]
