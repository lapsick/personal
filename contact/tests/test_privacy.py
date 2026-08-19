"""Privacy tests for contact handling: retention, notice, no body logging (T048)."""

import logging
import time
from datetime import timedelta

import pytest
from django.core import signing
from django.core.management import call_command
from django.utils import timezone
from wagtail.contrib.forms.models import FormSubmission

from contact.forms import _SIGNING_SALT, HONEYPOT_FIELD_NAME, TIMESTAMP_FIELD_NAME

pytestmark = pytest.mark.django_db


def _post_data(**overrides) -> dict:
    data = {
        "name": "Ada",
        "email": "ada@example.com",
        "message": "SECRET-BODY-TOKEN please do not log me.",
        HONEYPOT_FIELD_NAME: "",
        TIMESTAMP_FIELD_NAME: signing.dumps(time.time() - 10, salt=_SIGNING_SALT),
    }
    data.update(overrides)
    return data


def test_privacy_notice_renders_before_the_form(client, contact_page):
    """The privacy notice (contact intro) renders adjacent to/above the form."""
    html = client.get(contact_page.url).content.decode()
    assert "store your message" in html
    assert html.index("store your message") < html.index("<form")


@pytest.mark.integration
def test_prune_command_deletes_old_submissions(contact_page):
    """The retention command deletes submissions past the retention window."""
    old = FormSubmission.objects.create(page=contact_page, form_data={"name": "Old"})
    FormSubmission.objects.filter(pk=old.pk).update(
        submit_time=timezone.now() - timedelta(days=400)
    )
    recent = FormSubmission.objects.create(page=contact_page, form_data={"name": "New"})

    call_command("prune_contact_submissions", days=365)

    remaining = set(FormSubmission.objects.values_list("pk", flat=True))
    assert old.pk not in remaining
    assert recent.pk in remaining


@pytest.mark.integration
def test_message_body_is_not_logged_on_send_failure(client, contact_page, monkeypatch, caplog):
    """A delivery failure must not write the message body to the logs (D11)."""

    def _boom(*args, **kwargs):
        raise RuntimeError("SMTP down")

    monkeypatch.setattr("contact.models.EmailMessage.send", _boom)

    with caplog.at_level(logging.WARNING):
        client.post(contact_page.url, data=_post_data())

    assert "SECRET-BODY-TOKEN" not in caplog.text
