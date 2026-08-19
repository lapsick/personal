"""Unit tests for contact form validation and no-JS spam protection (US1)."""

import time

import pytest
from django.core import signing

from contact.forms import (
    _SIGNING_SALT,
    HONEYPOT_FIELD_NAME,
    TIMESTAMP_FIELD_NAME,
)

pytestmark = pytest.mark.django_db


def _token(offset_seconds: float) -> str:
    """Return a signed render-timestamp ``offset_seconds`` in the past."""
    return signing.dumps(time.time() - offset_seconds, salt=_SIGNING_SALT)


def _valid_data(**overrides) -> dict:
    """Return valid POST data (form rendered 10s ago), applying any overrides."""
    data = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "message": "I'd like to discuss a .NET architecture engagement.",
        HONEYPOT_FIELD_NAME: "",
        TIMESTAMP_FIELD_NAME: _token(10),
    }
    data.update(overrides)
    return data


def _build_form(contact_page, data):
    return contact_page.get_form(data, page=contact_page, user=None)


def test_valid_submission_is_valid_and_not_spam(contact_page):
    """A complete, human-paced submission validates and is not flagged as spam."""
    form = _build_form(contact_page, _valid_data())
    assert form.is_valid()
    assert form.is_spam is False


def test_missing_email_reports_field_error(contact_page):
    """A missing required field fails validation and names the field (FR-016)."""
    form = _build_form(contact_page, _valid_data(email=""))
    assert not form.is_valid()
    assert "email" in form.errors


def test_invalid_email_format_reports_field_error(contact_page):
    """A malformed email fails validation on the email field (FR-016)."""
    form = _build_form(contact_page, _valid_data(email="not-an-email"))
    assert not form.is_valid()
    assert "email" in form.errors


def test_filled_honeypot_flags_spam_without_erroring(contact_page):
    """A filled honeypot marks the form as spam but does not invalidate it (FR-019)."""
    form = _build_form(contact_page, _valid_data(**{HONEYPOT_FIELD_NAME: "http://spam"}))
    assert form.is_valid()  # no user-visible error
    assert form.is_spam is True


def test_too_fast_submission_flags_spam(contact_page):
    """A submission faster than the fill threshold trips the time-trap (D5)."""
    form = _build_form(contact_page, _valid_data(**{TIMESTAMP_FIELD_NAME: _token(0)}))
    assert form.is_valid()
    assert form.is_spam is True


def test_tampered_timestamp_flags_spam(contact_page):
    """An unsigned/tampered timestamp is treated as spam (D5)."""
    form = _build_form(contact_page, _valid_data(**{TIMESTAMP_FIELD_NAME: "tampered"}))
    assert form.is_valid()
    assert form.is_spam is True


def test_errored_field_gets_aria_wiring(contact_page):
    """Errored fields expose ``aria-invalid``/``aria-describedby`` (WCAG AA)."""
    form = _build_form(contact_page, _valid_data(email=""))
    assert not form.is_valid()
    attrs = form.fields["email"].widget.attrs
    assert attrs.get("aria-invalid") == "true"
    assert attrs.get("aria-describedby") == f"{form['email'].auto_id}_error"
