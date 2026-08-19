"""Contact form with JavaScript-free spam protection (honeypot + time-trap).

Implements the spam rules from ``contracts/contact-form.md`` (D5): a visually
hidden honeypot field and a server-signed render timestamp. Neither mechanism
requires client-side JavaScript, and detected spam is flagged (not raised as a
validation error) so the caller can silently drop it without user-visible
friction (FR-019).
"""

import time

from django import forms
from django.conf import settings
from django.core import signing
from wagtail.contrib.forms.forms import BaseForm, FormBuilder

#: Name of the visually hidden honeypot field. A bot that fills every input
#: will populate it; genuine and assistive-tech users never see it.
HONEYPOT_FIELD_NAME = "homepage_url"

#: Name of the hidden field carrying the server-signed render timestamp.
TIMESTAMP_FIELD_NAME = "form_loaded_at"

#: Salt namespacing the timestamp signature.
_SIGNING_SALT = "contact.form.timestamp"


def sign_render_timestamp() -> str:
    """Return a signed token encoding the current server time.

    Returns:
        A signed string safe to embed in a hidden form field; verified on
        submit to enforce the minimum fill time (time-trap).
    """
    return signing.dumps(time.time(), salt=_SIGNING_SALT)


class SpamProtectionMixin:
    """Form mixin that adds honeypot + time-trap detection without hard-failing.

    Spam is recorded on ``is_spam`` rather than raised as a ``ValidationError``
    so the view can render a normal confirmation while dropping the submission,
    giving bots no signal (FR-019).
    """

    def __init__(self, *args, **kwargs):
        """Initialise the form and seed a fresh render timestamp on GET."""
        super().__init__(*args, **kwargs)
        self._is_spam = False
        if not self.is_bound and TIMESTAMP_FIELD_NAME in self.fields:
            self.fields[TIMESTAMP_FIELD_NAME].initial = sign_render_timestamp()

    @property
    def is_spam(self) -> bool:
        """Return whether the submission tripped the honeypot or time-trap."""
        return self._is_spam

    def full_clean(self):
        """Run validation, then wire ARIA error associations on errored fields.

        For each field with errors, mark it ``aria-invalid`` and point its
        ``aria-describedby`` at the error message the template renders, so the
        association is programmatic (WCAG 2.1 AA, seo-accessibility.md).
        """
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs["aria-invalid"] = "true"
                widget.attrs["aria-describedby"] = f"{self[name].auto_id}_error"

    def clean(self):
        """Validate normally, then flag (never raise on) spam signals."""
        cleaned_data = super().clean()

        # Honeypot: any non-empty value means a bot filled a hidden field.
        if (self.data.get(HONEYPOT_FIELD_NAME) or "").strip():
            self._is_spam = True
            return cleaned_data

        # Time-trap: reject submissions that arrive implausibly fast, or whose
        # signed timestamp is missing, tampered with, or expired.
        min_seconds = getattr(settings, "CONTACT_FORM_MIN_FILL_SECONDS", 2)
        max_age = getattr(settings, "CONTACT_FORM_MAX_AGE_SECONDS", 3600)
        token = self.data.get(TIMESTAMP_FIELD_NAME, "")
        try:
            rendered_at = signing.loads(token, salt=_SIGNING_SALT, max_age=max_age)
            if time.time() - float(rendered_at) < min_seconds:
                self._is_spam = True
        except (signing.BadSignature, ValueError, TypeError):
            self._is_spam = True

        return cleaned_data


class ContactFormBuilder(FormBuilder):
    """Form builder that injects the honeypot + timestamp fields and spam logic.

    The owner-defined fields (name, email, message) come from the page's
    ``FormField`` rows via the standard Wagtail form builder; this subclass adds
    the two spam-protection fields and mixes in :class:`SpamProtectionMixin`.
    """

    @property
    def formfields(self) -> dict:
        """Return the owner fields plus the hidden spam-protection fields."""
        fields = super().formfields
        fields[HONEYPOT_FIELD_NAME] = forms.CharField(
            required=False,
            label="Leave this field blank",
            widget=forms.TextInput(
                attrs={
                    "class": "hp-field",
                    "tabindex": "-1",
                    "autocomplete": "off",
                    "aria-hidden": "true",
                }
            ),
        )
        fields[TIMESTAMP_FIELD_NAME] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(),
        )
        return fields

    def get_form_class(self) -> type[BaseForm]:
        """Build the concrete form class with spam protection mixed in."""
        return type("ContactForm", (SpamProtectionMixin, BaseForm), self.formfields)
