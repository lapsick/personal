"""Curated StreamField block set for rich body content (data-model D4).

A small, consistent component vocabulary reused by ``ProjectPage`` and
``ArticlePage`` bodies. There is deliberately no raw-HTML block so rendered
output stays consistent and safe (Constitution Principle III).
"""

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StructBlock,
    TextBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class HeadingBlock(StructBlock):
    """A section heading rendered as an ``<h2>``/``<h3>`` within body content."""

    text = CharBlock(required=True, max_length=255, help_text="Heading text.")
    level = ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3")],
        default="h2",
        help_text="Semantic heading level (keep the document outline logical).",
    )

    class Meta:
        icon = "title"
        template = "core/blocks/heading_block.html"
        label = "Heading"


class CodeBlock(StructBlock):
    """A fenced code sample with an optional language label."""

    language = CharBlock(
        required=False,
        max_length=50,
        help_text="Language label shown above the code (e.g. csharp).",
    )
    code = TextBlock(required=True, help_text="Raw code; rendered verbatim.")

    class Meta:
        icon = "code"
        template = "core/blocks/code_block.html"
        label = "Code"


class ImageBlock(StructBlock):
    """An image with required alt text and an optional caption."""

    image = ImageChooserBlock(required=True)
    alt_text = CharBlock(
        required=True,
        max_length=255,
        help_text="Alternative text describing the image (accessibility).",
    )
    caption = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "image"
        template = "core/blocks/image_block.html"
        label = "Image"


class QuoteBlock(StructBlock):
    """A block quotation with an optional attribution."""

    quote = TextBlock(required=True)
    attribution = CharBlock(required=False, max_length=255)

    class Meta:
        icon = "openquote"
        template = "core/blocks/quote_block.html"
        label = "Quote"


def body_blocks() -> list[tuple[str, object]]:
    """Return the shared block list used by rich body StreamFields.

    Returns:
        A list of ``(name, block)`` tuples: heading, paragraph (rich text),
        code, image, and quote.
    """
    return [
        ("heading", HeadingBlock()),
        (
            "paragraph",
            RichTextBlock(
                features=["bold", "italic", "link", "ol", "ul", "document-link"],
                template="core/blocks/paragraph_block.html",
            ),
        ),
        ("code", CodeBlock()),
        ("image", ImageBlock()),
        ("quote", QuoteBlock()),
    ]
