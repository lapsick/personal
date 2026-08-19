"""Contact page: a Wagtail email-form page with no-JS spam protection.

Combines Wagtail's ``AbstractEmailForm`` (owner-editable fields, submission
storage, email notification) with the SEO fields from ``core.BasePage`` and the
honeypot/time-trap protection in ``contact.forms``. Spam is dropped silently and
email-send failures degrade to on-page fallback channels (FR-017..019).
"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.template.response import TemplateResponse
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField

from contact.forms import (
    HONEYPOT_FIELD_NAME,
    TIMESTAMP_FIELD_NAME,
    ContactFormBuilder,
)
from core.models import BasePage

logger = logging.getLogger(__name__)


class FormField(AbstractFormField):
    """An owner-editable field row for the contact form (name, email, message)."""

    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class ContactPage(AbstractEmailForm, BasePage):
    """Contact form page with honeypot + time-trap spam protection.

    Fields are owner-editable in Wagtail admin. On a valid, non-spam submission
    the owner is emailed (with the sender's address as reply-to) and the
    ``thank_you_text`` confirmation is shown; spam is dropped silently and a
    send failure shows fallback contact channels.
    """

    intro = RichTextField(
        blank=True,
        help_text="Lead-in shown above the form (include a short privacy notice).",
    )
    thank_you_text = RichTextField(
        blank=True,
        help_text="Confirmation shown after a successful submission (FR-017).",
    )

    form_builder = ContactFormBuilder

    content_panels = [
        *AbstractEmailForm.content_panels,
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address"),
                        FieldPanel("to_address"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            heading="Email notification",
        ),
    ]

    # SEO fields come from BasePage; keep its promote panels.
    promote_panels = BasePage.promote_panels

    max_count = 1

    def serve(self, request, *args, **kwargs):
        """Handle GET/POST: validate, drop spam silently, notify, or fall back.

        Overrides Wagtail's form serving to add three behaviours from the
        contact contract: detected spam renders the confirmation without
        persisting or emailing (FR-019); an email-send failure re-renders the
        form with fallback channels (FR-018); everything else follows the
        standard validate → persist → notify → confirm flow (FR-016/017).
        """
        if request.method == "POST":
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
            if form.is_valid():
                if getattr(form, "is_spam", False):
                    # Silently accept to the client; store/send nothing (FR-019).
                    return self.render_landing_page(request, None, *args, **kwargs)
                try:
                    submission = self.process_form_submission(form)
                except Exception:
                    # Do not log the message body (privacy, D11); surface a
                    # clear error plus fallback channels (FR-018).
                    logger.warning("Contact email delivery failed for page %s", self.pk)
                    context = self.get_context(request)
                    context["form"] = form
                    context["send_failed"] = True
                    return TemplateResponse(request, self.get_template(request), context)
                return self.render_landing_page(request, submission, *args, **kwargs)
        else:
            form = self.get_form(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form
        return TemplateResponse(request, self.get_template(request), context)

    def send_mail(self, form) -> None:
        """Email the owner the submission, using the sender's address as reply-to.

        Excludes the hidden spam-protection fields from the message body and
        never writes the body to the application logs (D11).

        Args:
            form: The validated contact form whose cleaned data is emailed.
        """
        addresses = [addr.strip() for addr in (self.to_address or "").split(",") if addr.strip()]
        if not addresses:
            return

        skip = {HONEYPOT_FIELD_NAME, TIMESTAMP_FIELD_NAME}
        lines = []
        for field in form:
            if field.name in skip:
                continue
            value = form.cleaned_data.get(field.name, "")
            lines.append(f"{field.label}: {value}")
        body = "\n".join(lines)

        reply_to = form.cleaned_data.get("email", "")
        email = EmailMessage(
            subject=self.subject or "New contact form submission",
            body=body,
            from_email=self.from_address or settings.DEFAULT_FROM_EMAIL,
            to=addresses,
            reply_to=[reply_to] if reply_to else None,
        )
        email.send(fail_silently=False)
