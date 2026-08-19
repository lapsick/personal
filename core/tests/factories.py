"""Shared factory_boy factories for Wagtail images and documents.

Page-type factories live in each app's own test package; these cover the media
models reused across apps (social images, resume document, article images).
"""

import factory
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from wagtail.documents.models import Document
from wagtail.images.models import Image

# A minimal valid 1x1 PNG (transparent) for image renditions in tests.
_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class ImageFactory(factory.django.DjangoModelFactory):
    """Create a Wagtail ``Image`` backed by a tiny in-memory PNG."""

    class Meta:
        model = Image

    title = factory.Sequence(lambda n: f"Test image {n}")

    @factory.lazy_attribute
    def file(self) -> SimpleUploadedFile:
        """Return a small valid PNG upload for the image file field."""
        return SimpleUploadedFile("test.png", _PNG_1X1, content_type="image/png")

    width = 1
    height = 1


class DocumentFactory(factory.django.DjangoModelFactory):
    """Create a Wagtail ``Document`` (e.g. a resume) with placeholder content."""

    class Meta:
        model = Document

    title = factory.Sequence(lambda n: f"Test document {n}")

    @factory.lazy_attribute
    def file(self) -> ContentFile:
        """Return a small placeholder file for the document."""
        return ContentFile(b"%PDF-1.4 test", name="resume.pdf")
