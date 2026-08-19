"""Page models for the blog: index + article pages, with tagging.

Implements the Article entity (data-model.md): ``ArticlePage`` is directly
linkable/shareable and ``BlogIndexPage`` lists articles most-recent-first with a
graceful empty state.
"""

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField

from core.blocks import body_blocks
from core.models import BasePage
from core.utils import list_token as _list_token


class ArticleTag(TaggedItemBase):
    """Through model linking a tag to an ``ArticlePage``."""

    content_object = ParentalKey(
        "blog.ArticlePage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class BlogIndexPage(BasePage):
    """Lists child ``ArticlePage`` items newest-first, with an empty state."""

    intro = models.TextField(blank=True, help_text="Optional lead-in for the article list.")

    content_panels = [
        *BasePage.content_panels,
        FieldPanel("intro"),
    ]

    subpage_types = ["blog.ArticlePage"]
    max_count = 1

    def get_articles(self):
        """Return live child articles, most recent first (by ``date``)."""
        return (
            ArticlePage.objects.child_of(self)
            .live()
            .order_by("-date", "-first_published_at")
            .specific()
        )

    def get_context(self, request, *args, **kwargs) -> dict:
        """Add the ordered article list and a fragment-cache token to context.

        ``list_token`` changes whenever a child article is added or edited, so
        the cached list fragment never serves stale content.
        """
        context = super().get_context(request, *args, **kwargs)
        context["articles"] = self.get_articles()
        context["list_token"] = _list_token(ArticlePage.objects.child_of(self).live())
        return context


class ArticlePage(BasePage):
    """A single technical article: title, date, summary, body, tags, image."""

    date = models.DateField(help_text="Publication date (ordering and display).")
    summary = models.TextField(help_text="List summary and default meta description.")
    body = StreamField(body_blocks(), help_text="Article content.")
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Header image and social card.",
    )

    content_panels = [
        *BasePage.content_panels,
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("summary"),
                FieldPanel("featured_image"),
                FieldPanel("tags"),
            ],
            heading="Article metadata",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types: list[str] = []

    #: Open Graph object type for articles (used by the SEO head partial).
    og_type = "article"

    def get_social_image(self):
        """Prefer an explicit social image, falling back to the featured image."""
        return self.social_image or self.featured_image
