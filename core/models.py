"""Shared model building blocks: ``BasePage`` SEO mixin and ``SiteSettings``.

These are the cross-cutting pieces every page family depends on (data-model.md):
an abstract page carrying the SEO/social contract and an owner-editable global
settings model surfaced in the header, footer, and SEO metadata.
"""

from django.db import models
from django.utils.safestring import SafeString, mark_safe
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.models import Orderable, Page


class BasePage(Page):
    """Abstract page carrying the shared SEO + social-sharing contract (D7).

    Concrete page types inherit from this so every page can emit a canonical
    URL and an Open Graph / Twitter card image on top of Wagtail's built-in
    ``seo_title`` and ``search_description`` fields.
    """

    social_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image used for social/link previews (Open Graph, Twitter).",
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Override the canonical URL. Defaults to this page's own URL.",
    )

    promote_panels = [
        *Page.promote_panels,
        MultiFieldPanel(
            [
                FieldPanel("social_image"),
                FieldPanel("canonical_url"),
            ],
            heading="SEO & social sharing",
        ),
    ]

    class Meta:
        abstract = True

    def get_canonical_url(self) -> str:
        """Return the canonical URL for this page.

        Returns:
            The explicit ``canonical_url`` override when set, otherwise the
            page's own full (absolute) URL.
        """
        return self.canonical_url or (self.full_url or "")

    def get_social_image(self):
        """Return the image to use for social/link previews, or ``None``.

        Subclasses with their own ``featured_image`` may override this to
        provide a fallback.
        """
        return self.social_image


class SocialProfile(Orderable):
    """An additional professional profile link shown in the site footer."""

    settings = ParentalKey(
        "core.SiteSettings",
        on_delete=models.CASCADE,
        related_name="other_profiles",
    )
    label = models.CharField(max_length=100, help_text="e.g. Mastodon, Stack Overflow.")
    url = models.URLField()

    panels = [
        FieldPanel("label"),
        FieldPanel("url"),
    ]


@register_setting
class SiteSettings(BaseGenericSetting, ClusterableModel):
    """Owner-editable global data surfaced across every page (data-model.md).

    Provides identity fields (name, title, tagline), the downloadable resume,
    and the fallback contact channels used by the contact page and footer.
    """

    owner_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Full name, used in the header, footer, and SEO metadata.",
    )
    professional_title = models.CharField(
        max_length=150,
        blank=True,
        help_text='e.g. "Software Engineer & Architect".',
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short specialization line (e.g. Microsoft/.NET focus).",
    )
    resume_document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Downloadable resume (re-upload in admin to update it).",
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Fallback contact address (obfuscated when rendered).",
    )
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("owner_name"),
                FieldPanel("professional_title"),
                FieldPanel("tagline"),
            ],
            heading="Identity",
        ),
        FieldPanel("resume_document"),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("linkedin_url"),
                FieldPanel("github_url"),
                InlinePanel("other_profiles", label="Other profiles"),
            ],
            heading="Contact & profiles",
        ),
    ]

    class Meta:
        verbose_name = "Site settings"

    @property
    def obfuscated_contact_email(self) -> SafeString:
        """Return the contact email HTML-entity-encoded to deter scrapers.

        Every character is emitted as a numeric HTML entity (FR-025) so the
        address is not present as harvestable plain text in the markup, while
        still rendering and being clickable for humans. Returns an empty
        (safe) string when no contact email is set.
        """
        if not self.contact_email:
            return mark_safe("")  # noqa: S308 - empty constant, not user input
        encoded = "".join(f"&#{ord(char)};" for char in self.contact_email)
        return mark_safe(encoded)  # noqa: S308 - numeric entities only, no markup

    @property
    def obfuscated_mailto(self) -> SafeString:
        """Return an entity-encoded ``mailto:`` href for the contact email."""
        if not self.contact_email:
            return mark_safe("")  # noqa: S308 - empty constant, not user input
        encoded = "".join(f"&#{ord(char)};" for char in f"mailto:{self.contact_email}")
        return mark_safe(encoded)  # noqa: S308 - numeric entities only, no markup
