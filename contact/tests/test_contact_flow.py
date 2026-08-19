"""Integration tests for the contact submission flow (User Story 1).

Exercises the full ``POST /contact/`` round-trip: valid submit → email queued +
confirmation; forced send failure → fallback channels (contract: contact-form.md).
"""

import time

import pytest
from django.core import mail, signing

from contact.forms import _SIGNING_SALT, HONEYPOT_FIELD_NAME, TIMESTAMP_FIELD_NAME
from core.models import SiteSettings

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _post_data(**overrides) -> dict:
    data = {
        "name": "Grace Hopper",
        "email": "grace@example.com",
        "message": "Interested in a systems architecture review.",
        HONEYPOT_FIELD_NAME: "",
        TIMESTAMP_FIELD_NAME: signing.dumps(time.time() - 10, salt=_SIGNING_SALT),
    }
    data.update(overrides)
    return data


def test_valid_submission_notifies_owner_and_confirms(client, contact_page):
    """A valid POST queues one owner email (reply-to sender) and shows thanks."""
    response = client.post(contact_page.url, data=_post_data())

    assert response.status_code == 200
    assert b"sent" in response.content.lower()
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.to == ["owner@example.com"]
    assert sent.reply_to == ["grace@example.com"]
    # The message body is included for the owner...
    assert "systems architecture review" in sent.body
    # ...but the hidden spam fields are not.
    assert HONEYPOT_FIELD_NAME not in sent.body


def test_spam_submission_is_dropped_silently(client, contact_page):
    """A honeypot-filled POST shows success but sends/stores nothing (FR-019)."""
    response = client.post(contact_page.url, data=_post_data(**{HONEYPOT_FIELD_NAME: "bot"}))

    assert response.status_code == 200
    assert len(mail.outbox) == 0
    assert contact_page.get_submission_class().objects.count() == 0


def test_send_failure_shows_fallback_channels(client, contact_page, monkeypatch):
    """A delivery failure re-renders the form with fallback channels (FR-018)."""
    settings_obj = SiteSettings.load(request_or_site=None)
    settings_obj.contact_email = "owner@example.com"
    settings_obj.linkedin_url = "https://www.linkedin.com/in/example"
    settings_obj.save()

    def _boom(*args, **kwargs):
        raise RuntimeError("SMTP down")

    monkeypatch.setattr("contact.models.EmailMessage.send", _boom)

    response = client.post(contact_page.url, data=_post_data())

    assert response.status_code == 200
    assert b"alternative contact methods" in response.content.lower()
    assert b"linkedin" in response.content.lower()


def test_invalid_submission_rerenders_with_error(client, contact_page):
    """A missing email re-renders the form (200) with a field error (FR-016)."""
    response = client.post(contact_page.url, data=_post_data(email=""))

    assert response.status_code == 200
    assert len(mail.outbox) == 0
    assert b"correct the following" in response.content.lower()
