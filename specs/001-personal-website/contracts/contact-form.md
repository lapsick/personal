# Contract: Contact Form

**Feature**: 001-personal-website | **Date**: 2026-08-18

Defines the request/response contract, validation rules, spam protection, and email/notification
behavior for the contact path. Implements FR-015..FR-019, FR-025, and D5/D11.

## Endpoint

`POST /contact/` (same URL as the `GET` contact page; Wagtail form page handles both).

Content type: `application/x-www-form-urlencoded` (standard HTML form, no JS required).

## Request fields

| Field | Visible | Required | Rule |
|-------|---------|----------|------|
| `name` | yes | yes | non-empty, trimmed, length ≤ 100 |
| `email` | yes | yes | valid email format; used as reply-to |
| `message` | yes | yes | non-empty; length 1..5000 |
| `csrfmiddlewaretoken` | no | yes | Django CSRF token |
| `<honeypot>` | no (CSS/`aria-hidden`) | must be empty | any value ⇒ spam |
| `<form_rendered_at>` | no (hidden, signed) | yes | server-signed timestamp of GET render |

Honeypot and timestamp field names SHOULD be non-obvious and are implementation detail; they MUST
NOT be announced to assistive tech (`aria-hidden="true"`, `tabindex="-1"`, `autocomplete="off"`).

## Validation & processing order (server-side)

1. **CSRF** check (Django). Fail ⇒ 403.
2. **Spam — honeypot**: honeypot non-empty ⇒ treat as accepted to the client (show success or
   drop silently) but do **not** persist or email. No user-visible friction (FR-019).
3. **Spam — time-trap**: `now - form_rendered_at < MIN_FILL_SECONDS` (default 2s) or signature
   invalid/expired ⇒ reject as spam, same silent handling (FR-019).
4. **Field validation**: required + formats (above). Any failure ⇒ re-render form (HTTP 200) with
   field-level errors naming the field(s) to fix (FR-016). No data sent.
5. **Persist** submission per retention policy (D11) — minimized fields only; message body never
   written to application logs (FR-025/privacy).
6. **Notify owner**: send email to `ContactPage.to_address` with `name`, `email` (reply-to), and
   `message` (FR-017).
7. **Confirm**: render `thank_you_text` confirmation (FR-017).

## Responses

| Outcome | HTTP | Body |
|---------|------|------|
| Valid + sent | 200 | Confirmation (`thank_you_text`) — immediate acknowledgement (FR-017, SC-003) |
| Validation error | 200 | Form re-rendered with per-field errors (FR-016) |
| Send/delivery failure | 200 | Clear error message + fallback channels: `SiteSettings.contact_email`, LinkedIn/GitHub links (FR-018) |
| Detected spam | 200 | Indistinguishable from success (no bot feedback), nothing persisted/emailed (FR-019) |
| CSRF failure | 403 | Standard CSRF error page |

## Non-functional rules

- **No JavaScript required** for any step (progressive enhancement). Optional JS may add inline
  validation hints but MUST NOT be required for submission.
- **Accessibility** (WCAG 2.1 AA): each input has an associated `<label>`; errors are associated via
  `aria-describedby` and summarized at the top of the form; submit is keyboard-operable; success and
  error states are conveyed in text, not by color alone (see `seo-accessibility.md`).
- **Privacy** (D11): data minimization; retention limit on stored submissions; privacy notice
  rendered adjacent to the form; HTTPS only; message body excluded from logs.
- **Performance**: submission round-trip completes well within the SC-003 budget (visitor completes
  and submits in < 60s; ≥95% of valid submissions notify the owner).

## Test hooks (see quickstart.md & plan D10)

- Unit: honeypot-filled ⇒ not persisted/emailed; sub-threshold timing ⇒ rejected; missing/invalid
  field ⇒ specific error; valid input ⇒ email built with correct reply-to.
- Integration (`@pytest.mark.integration`): full POST with valid data ⇒ 1 email queued + confirmation
  rendered; forced send failure ⇒ fallback channels shown.
