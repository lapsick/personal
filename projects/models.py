"""Page models for the projects section: index + individual project pages.

Implements the Work Item entity (data-model.md): each ``ProjectPage`` carries
the problem/role/approach/technologies/outcome content model plus safe external
links, and ``ProjectIndexPage`` lists them with a graceful empty state.
"""

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Orderable

from core.blocks import body_blocks
from core.models import BasePage
from core.utils import list_token as _list_token


class ProjectTag(TaggedItemBase):
    """Through model linking a technology tag to a ``ProjectPage``."""

    content_object = ParentalKey(
        "projects.ProjectPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class ProjectIndexPage(BasePage):
    """Lists child ``ProjectPage`` cards, with an empty state when none exist."""

    intro = models.TextField(blank=True, help_text="Optional lead-in for the projects list.")

    content_panels = [
        *BasePage.content_panels,
        FieldPanel("intro"),
    ]

    subpage_types = ["projects.ProjectPage"]
    max_count = 1

    def get_projects(self):
        """Return live child project pages, newest first, with tags prefetched.

        Prefetching the tag through-model keeps the listing query count flat as
        the number of projects grows (no N+1 on technology tags, Principle IV).
        """
        return (
            ProjectPage.objects.child_of(self)
            .live()
            .order_by("-date", "-first_published_at")
            .specific()
            .prefetch_related("technologies")
        )

    def get_context(self, request, *args, **kwargs) -> dict:
        """Add the ordered project list and a fragment-cache token to context.

        ``list_token`` changes whenever a child project is added or edited, so
        the cached list fragment never serves stale content.
        """
        context = super().get_context(request, *args, **kwargs)
        context["projects"] = self.get_projects()
        context["list_token"] = _list_token(ProjectPage.objects.child_of(self).live())
        return context


class ProjectPage(BasePage):
    """A single project: problem, role, approach, technologies, outcome, links."""

    summary = models.TextField(help_text="Short description for cards and previews.")
    problem = models.TextField(help_text="The problem or context the project addressed.")
    role = models.TextField(help_text="The owner's role and contribution.")
    approach = StreamField(body_blocks(), help_text="How the problem was solved.")
    outcome = models.TextField(help_text="The result or impact.")
    technologies = ClusterTaggableManager(
        through=ProjectTag,
        blank=True,
        help_text="Technology stack (comma-separated tags).",
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    date = models.DateField(
        null=True,
        blank=True,
        help_text="Project date (used for ordering, newest first).",
    )

    content_panels = [
        *BasePage.content_panels,
        FieldPanel("summary"),
        FieldPanel("featured_image"),
        MultiFieldPanel(
            [
                FieldPanel("problem"),
                FieldPanel("role"),
                FieldPanel("approach"),
                FieldPanel("outcome"),
            ],
            heading="Case study",
        ),
        FieldPanel("technologies"),
        InlinePanel("external_links", label="External links"),
        FieldPanel("date"),
    ]

    parent_page_types = ["projects.ProjectIndexPage"]
    subpage_types: list[str] = []

    def get_social_image(self):
        """Prefer an explicit social image, falling back to the featured image."""
        return self.social_image or self.featured_image


class ProjectExternalLink(Orderable):
    """A labelled external link (live site, repo, case study) for a project."""

    project = ParentalKey(
        ProjectPage,
        on_delete=models.CASCADE,
        related_name="external_links",
    )
    label = models.CharField(max_length=100, help_text="e.g. Live site, Source, Case study.")
    url = models.URLField(help_text="Destination URL (validated).")

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
    ]
