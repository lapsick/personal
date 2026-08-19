# Phase 0 Research: Personal Professional Website

**Feature**: 001-personal-website | **Date**: 2026-08-18

All decisions below were chosen to satisfy the spec's requirements and the project constitution
while honoring the stack directives in the plan input. No unresolved `NEEDS CLARIFICATION` remain.

---

## D1. CMS & framework versions

**Decision**: Django **5.2 LTS** + Wagtail **7.4 LTS**, on Python **3.12**.

**Rationale**: Wagtail 7.4 is the current LTS (released May 2026, security-supported through
Nov 2027) and pairs with Django's current LTS. LTS-on-LTS maximizes the maintenance window for a
site the owner will keep for years with minimal churn. CodeRed Cloud provides Python 3.6–3.13;
3.12 has mature wheels for all dependencies and is comfortably within Wagtail 7.4's supported range.

**Alternatives considered**:
- *Latest non-LTS Wagtail (7.x newest)*: shorter support window, more frequent breaking upgrades —
  rejected for a low-maintenance personal site.
- *Plain Django + django CMS / no CMS*: fails the owner-maintainable principle (FR-024) as cleanly
  as Wagtail's page tree + admin does.
- *coderedcms (Wagtail CRX)*: CodeRed's own Wagtail distribution; adds opinionated page types and
  weight beyond what 5 pages need. Plain Wagtail keeps the model small and the content model exactly
  matches the spec. Rejected as unnecessary scope.

**Sources**: [Wagtail EOL/LTS](https://endoflife.date/wagtail),
[Wagtail release process](https://docs.wagtail.org/en/stable/releases/release_process.html).

---

## D2. Static files — WhiteNoise vs. platform-native serving

**Decision**: Include **WhiteNoise** with `CompressedManifestStaticFilesStorage`, as directed in the
plan input, while documenting that CodeRed Cloud serves static files natively in production.

**Rationale**: CodeRed Cloud's docs explicitly state it "automatically finds your static files, and
serves them from the filesystem using a fast native web server. Shims such as `whitenoise` are not
needed." In production the platform intercepts `/static/` before Django, so WhiteNoise is redundant
*there*. It is still valuable because it (a) provides hashed, long-cache, compressed static storage
for cache-busting regardless of host, (b) lets local/other-host runs serve static without a separate
web server (prod-parity testing), and (c) keeps the site host-portable if CodeRed is ever swapped.
It is inert and harmless under CodeRed's native serving. Net: keep it, document the redundancy.

**Alternatives considered**:
- *Drop WhiteNoise, rely solely on CodeRed*: fewer deps, but loses host portability and local
  prod-parity, and contradicts the explicit plan directive. Rejected.

**Source**: [CodeRed Django deployments](https://www.codered.cloud/docs/django/deployments/).

---

## D3. Deployment configuration for CodeRed Cloud

**Decision**: Structure settings as `portfolio/settings/{base,dev,prod}.py`. Provide `prod.py`
(required exact name) and `portfolio/wsgi.py` (required). Deploy via the `cr` CLI
(`pip install cr`, `cr login`, `cr check <app>`, `cr deploy <app>`). Use `psycopg[binary]` against
the platform's PostgreSQL 15. Read `SECRET_KEY`, database credentials, and `ALLOWED_HOSTS` from
environment variables (the platform cycles `RANDOM_SECRET_KEY` and DB passwords on deploy).

**Rationale**: These are CodeRed Cloud's documented, non-optional conventions. `cr check` scans the
project and fixes settings for platform compatibility, reducing deployment risk. HTTPS/SSL is issued
automatically; media and database receive daily backups — directly satisfying the spec's HTTPS and
daily-backup requirements without custom infrastructure.

**Alternatives considered**:
- *Single `settings.py` toggled by env*: CodeRed expects the `settings/prod.py` module path;
  splitting is the path of least resistance and keeps dev (SQLite/DEBUG) cleanly separate. Adopted.
- *`dj-database-url` / `DATABASE_URL`*: convenient, but the platform exposes discrete DB env vars;
  `cr check` targets the discrete form. Use discrete env vars to match the platform.

**Sources**: [Host software](https://www.codered.cloud/reference/host-software/),
[Wagtail quickstart](https://www.codered.cloud/docs/wagtail/quickstart/),
[Django deployments](https://www.codered.cloud/docs/django/deployments/).

---

## D4. Content modeling in Wagtail

**Decision**: Model each page family as Wagtail page types under the site's page tree:
- `HomePage` (landing) and `AboutPage` — editable singleton-style pages.
- `ProjectIndexPage` → child `ProjectPage`s (fields: problem, role, approach, technologies,
  outcome, external links, optional image).
- `BlogIndexPage` → child `ArticlePage`s (fields: title, publish date, summary, body, tags).
- `ContactPage` — a Wagtail form page (see D5).
Rich body content uses **StreamField** with a small, curated block set (heading, rich text, code,
image, quote) so articles/projects are flexible yet consistent. Tags use Wagtail's taggit
integration (`ClusterTaggableManager`).

**Rationale**: Page types + Wagtail admin satisfy FR-024 (owner edits all content, adds
projects/articles, no code changes) and FR-004 (each page/article has a stable, shareable URL via
Wagtail's routable page tree). StreamField keeps rich content editable without raw HTML while
enforcing a consistent component vocabulary (Principle III). Index pages provide the list views
(FR-009, FR-012) and their empty states (FR-011, FR-014).

**Alternatives considered**:
- *Django models + custom admin*: reinvents Wagtail's page tree, preview, drafts, and URL routing.
  Rejected.
- *Wagtail Snippets for projects/articles*: snippets lack their own URL/preview by default; page
  types give shareable addresses for free. Rejected for the primary content types.

---

## D5. Contact form: validation, spam protection, no-JS operation

**Decision**: Implement `ContactPage` as a Wagtail form page (subclass of `AbstractEmailForm`) with
server-side validation and **JavaScript-free** spam protection combining:
1. A **honeypot** field — visually hidden, `aria-hidden`, `autocomplete="off"`; any non-empty value
   silently rejects the submission.
2. A **time-trap** — a signed timestamp rendered into the form; submissions faster than a small
   threshold (e.g., < 2s) are treated as bots.
On success: send an email notification to the owner (platform email backend) and show an on-page
confirmation. On failure: show field-level errors (FR-016) and, on send/delivery failure, a clear
error plus fallback contact channels (email + profile links) (FR-018).

**Rationale**: Honeypot + time-trap require no client JS and add no friction for genuine or
assistive-technology users, satisfying progressive enhancement and WCAG (no CAPTCHA barrier).
`AbstractEmailForm` keeps the contact page and its fields owner-editable in Wagtail admin. Server-side
validation covers required fields and email format (FR-015/016). Email is the notification channel
(FR-017); CodeRed provides zero-config email sending.

**Alternatives considered**:
- *Google reCAPTCHA / hCaptcha*: requires JS, adds a third-party dependency and an accessibility/
  privacy burden; violates the no-JS-core and privacy goals. Rejected as the primary mechanism
  (may be added later behind config if abuse warrants).
- *Akismet spam check*: effective but adds an external API dependency and sends message content to a
  third party (privacy tension). Documented as an optional future hardening, off by default.

---

## D6. Resume as a downloadable asset

**Decision**: Store the resume as a **Wagtail Document** (uploaded via admin) and link to it from
Home/About. Serve via Wagtail's document-serving view.

**Rationale**: Keeps the resume owner-maintainable (re-upload a new PDF in admin, link stays stable)
per FR-024, and it is included in the platform's daily media backups. Avoids committing a binary to
source or hardcoding a static path.

**Alternatives considered**:
- *Static file in the repo*: requires a code deploy to update the resume — fails owner-maintainable.
  Rejected.

---

## D7. SEO, sitemap, and social sharing

**Decision**: Use `wagtail.contrib.sitemaps` (or Django's sitemap framework) for `/sitemap.xml`,
add a `robots.txt`, and add a reusable **SEO head partial** producing per-page `<title>`, meta
description, canonical URL, and Open Graph / Twitter Card tags. Provide a `SeoMixin`/`BasePage`
carrying `search_description`, social image, and canonical fields editable in admin.

**Rationale**: Satisfies FR-023 (discoverable + correct link previews) and SC-008/SC-009. Wagtail
pages already expose `seo_title`/`search_description`; the mixin extends this with OG/Twitter and a
social image so every page and article renders a descriptive shareable card.

**Alternatives considered**:
- *`wagtail-metadata` package*: convenient but an extra dependency for what a small mixin covers.
  Start with the mixin; adopt the package only if metadata needs grow.

---

## D8. Accessibility (WCAG 2.1 AA) approach

**Decision**: Semantic HTML5 landmarks, a visible skip-to-content link, labeled form controls with
programmatically associated errors (`aria-describedby`), visible focus states, AA color-contrast
tokens, alt text on images (enforced in admin), and full keyboard operability of nav and the contact
form. Verify with automated checks (axe-core / pa11y) in CI against key pages and manual keyboard +
screen-reader passes.

**Rationale**: Directly encodes FR-022 and SC-004. Server-rendered semantic markup + progressive
enhancement is inherently accessible; automated + manual checks form the acceptance gate.

**Alternatives considered**:
- *Manual-only auditing*: not repeatable; automated checks in CI catch regressions. Adopted both.

---

## D9. Performance / Core Web Vitals approach

**Decision**: Mobile-first responsive CSS with minimal/no render-blocking JS; system font stack or
a single self-hosted variable font with `font-display: swap`; Wagtail responsive image renditions
(`srcset`, width/height to prevent CLS); template-fragment caching for nav and list pages;
`select_related`/`prefetch_related` to hold per-page DB queries within a documented budget
(no N+1 on index pages). Track a per-page-type query-count assertion in tests.

**Rationale**: Encodes the plan's CWV budget (LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms → SC-005) and
Principle IV (no needless quadratic / N+1, benchmark-guarded). Sized images with explicit
dimensions are the dominant CLS/LCP lever for a content site.

**Alternatives considered**:
- *Client-side hydration / SPA*: unnecessary weight, hurts CWV and the no-JS requirement. Rejected.

---

## D10. Testing strategy (Constitution II)

**Decision**: `pytest` + `pytest-django`, `factory_boy` for Wagtail page fixtures, `pytest-cov` with
`--cov-fail-under=80` in CI. **Unit tests** (models, form validation incl. honeypot/time-trap logic,
SEO mixin, template tags) run isolated with the email backend faked and no network. **Integration
tests** (full contact-submission POST → email queued, page routing, sitemap, index empty-states) are
tagged `@pytest.mark.integration` and run as a separate CI job. Every bug fix adds a failing→passing
regression test.

**Rationale**: Encodes Principle II exactly (happy + edge/error paths, isolated units, tagged
integration, ≥80% non-decreasing coverage).

**Alternatives considered**:
- *Django `TestCase` only*: workable, but `pytest`'s markers/fixtures give cleaner unit/integration
  separation the constitution requires. Adopted pytest.

---

## D11. Privacy-compliant contact-data handling

**Decision**: Data minimization (collect only name, reply-to email, message); publish a short
privacy notice on/near the contact form describing purpose, storage, and retention; set a retention
limit for stored submissions (Wagtail stores form submissions — periodically prune, or email-only
with short DB retention); serve everything over HTTPS (platform-provided); never log message bodies.

**Rationale**: Satisfies FR-025-adjacent privacy assumptions in the spec and the "privacy-compliant
handling" plan directive. Minimization + retention limit + notice is the baseline for personal-data
collection regardless of specific jurisdiction (exact regulatory scope deferred per spec).

**Alternatives considered**:
- *Store all submissions indefinitely*: unnecessary personal-data liability. Rejected in favor of a
  retention policy.

---

## Resolved unknowns summary

| Topic | Resolution |
|-------|-----------|
| Framework/versions | Django 5.2 LTS, Wagtail 7.4 LTS, Python 3.12 |
| Static files | WhiteNoise kept (portability/prod-parity); CodeRed serves natively in prod |
| Deploy target config | `settings/prod.py` + `wsgi.py`, `cr` CLI, PostgreSQL 15, env-var secrets |
| Content model | Wagtail page types + StreamField + taggit |
| Contact spam protection | Honeypot + time-trap (no JS); Akismet optional/off |
| Resume | Wagtail Document (owner-uploadable) |
| SEO | sitemap.xml + robots.txt + SEO head partial/mixin (OG/Twitter) |
| Accessibility | Semantic HTML + axe/pa11y CI + manual keyboard/SR passes |
| Performance | Renditions, sized images, fragment cache, query budget |
| Testing | pytest, 80% coverage gate, tagged integration |
| Privacy | Minimization + retention limit + notice + HTTPS |
| Analytics (spec-deferred) | Out of scope for v1; if added, use privacy-respecting, cookieless analytics |
