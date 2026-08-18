# Implementation Plan: Personal Professional Website

**Branch**: `001-personal-website` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-personal-website/spec.md`

## Summary

A server-rendered personal/professional website for a Software Engineer & Architect specializing
in the Microsoft/.NET stack, whose primary goal is converting qualified visitors (recruiters,
CTOs, clients, engineers, event organizers) into contacts, with a secondary goal of building a
reputation via technical writing.

**Technical approach**: Build a single Django project using **Wagtail** as the CMS so every page
(Home, About, Projects, Blog, Contact) is editable by the owner through Wagtail's admin with no
code changes. Projects and Articles are modeled as Wagtail page types carrying the spec's content
model. Pages render with Django templates using progressive enhancement — all core content and the
contact path work without JavaScript. The contact form uses server-side validation plus no-JS spam
protection (honeypot + time-trap). Non-functional gates from the spec (WCAG 2.1 AA, good Core Web
Vitals, responsive, SEO + sitemap, privacy-compliant contact handling) are designed in. Storage is
PostgreSQL in production and SQLite locally; the resume is a Wagtail Document (owner-uploadable).
Deployment targets **CodeRed Cloud's free tier** (managed Django/Wagtail on Azure) with automatic
HTTPS and daily backups.

## Technical Context

**Language/Version**: Python 3.12 (CodeRed Cloud offers Python 3.6–3.13; 3.12 chosen for broad
wheel availability and Wagtail 7.4 support)

**Primary Dependencies**: Django 5.2 LTS, Wagtail 7.4 LTS (security-supported through Nov 2027),
`psycopg[binary]` (PostgreSQL driver), `whitenoise` (static files — see research note),
`pip-tools` (dependency locking). Dev/test: `pytest`, `pytest-django`, `pytest-cov`,
`factory_boy`, `ruff`, `mypy`, `django-stubs`, `pre-commit`.

**Storage**: PostgreSQL 15 in production (provided by CodeRed Cloud), SQLite for local development.
Media (images, resume document) stored via Wagtail's document/image models; served by the platform
in prod, included in daily backups.

**Testing**: `pytest` + `pytest-django` with `pytest-cov`; unit tests isolated (no network),
integration tests tagged via a `@pytest.mark.integration` marker; minimum 80% line coverage enforced
in CI.

**Target Platform**: Linux server (managed uWSGI on CodeRed Cloud / Azure); responsive HTML for all
viewport widths 320px–1920px; mobile-first.

**Project Type**: Server-rendered web application (single Django project, multiple Wagtail apps).

**Performance Goals**: Meet "good" Core Web Vitals — LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms on a
mid-range mobile device over a typical mobile connection (maps to spec SC-005). No N+1 query
regressions on list pages; page-render DB query budget documented per page type.

**Constraints**: Core content and the contact path MUST function with JavaScript disabled
(progressive enhancement). No client-side framework. WCAG 2.1 AA. Contact form data handled
privacy-compliantly (data minimization, retention limit, privacy notice). No secrets in source.

**Scale/Scope**: Single-owner site; 5 top-level pages + 0..N projects + 0..N articles. Low traffic
(personal site), free-tier resource envelope. ~4–6 Wagtail apps, ~10–15 templates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution (`.specify/memory/constitution.md`, v1.0.0) is Python-oriented; this plan is a
Python (Django/Wagtail) project, so all principles apply directly and no framework mismatch exists.

| Principle | Gate | How this plan satisfies it | Status |
|-----------|------|----------------------------|--------|
| I. Code Quality | `ruff format` + `ruff` lint zero-error; `mypy` (with `django-stubs`) passes on new/modified modules; docstrings on public modules/classes/functions; single responsibility | Ruff + mypy configured in `pyproject.toml`; enforced by pre-commit and CI; Wagtail models/blocks/forms documented | PASS |
| II. Testing (NON-NEGOTIABLE) | pytest happy + edge/error paths; regression test per bug fix; ≥80% line coverage in CI, non-decreasing; unit tests isolated (no network); integration tagged separately | `pytest`/`pytest-django`; per-app tests; `@pytest.mark.integration` for DB/email/HTTP flows; `pytest-cov --cov-fail-under=80` in CI; email backend faked in unit tests | PASS |
| III. UX Consistency | One consistent format across user-facing surfaces; breaking changes versioned/documented; error messages say what failed + how to fix | Single base template + shared components; consistent form-error rendering; consistent, styled 404/500 pages; navigation identical on every page (FR-002/003) | PASS (mapped to HTML surfaces — see research) |
| IV. Performance | Benchmark performance-sensitive paths; regression >10% blocks merge; avoid needless quadratic; batch/stream I/O | Core Web Vitals budget + per-page DB query budget (no N+1 via `select_related`/`prefetch_related`); Wagtail image renditions; template-fragment caching for nav/lists | PASS |
| Python Environment Standards | Pin Python version; lockfile; isolated venv; evaluate new deps | Python pinned to 3.12 (CI + prod); `requirements.txt` compiled/pinned from `requirements.in` via `pip-tools`; venv-only installs; deps limited to maintained, permissively licensed packages | PASS |
| Development Workflow & Quality Gates | PR review ≥1 approval; CI runs lint + typecheck + full tests; pre-commit auto-fix | GitHub Actions CI (ruff, mypy, pytest+coverage); `.pre-commit-config.yaml` runs ruff + mypy before commit; branch-per-feature already in place | PASS |

**Result**: No violations. Complexity Tracking table intentionally left empty.

**Post-design re-check (after Phase 1)**: The generated design (`data-model.md`, `contracts/`,
`quickstart.md`) introduces no new violations — small single-responsibility Wagtail apps, a testable
contact-form contract with isolated-unit vs. tagged-integration coverage, an 80% coverage gate, and
documented performance/query budgets all remain within the gates above. Gate re-confirmed: **PASS**.

**Interpretation note (Principle III)**: The constitution frames UX consistency around CLI/API
output modes. For a server-rendered site the analogous "user-facing surfaces" are the HTML
templates, form validation messages, and error pages; consistency is enforced through a single base
layout, shared partials, and one form-error rendering convention. Recorded in `research.md`.

## Project Structure

### Documentation (this feature)

```text
specs/001-personal-website/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── routes.md            # URL / page-type routing contract
│   ├── contact-form.md      # Contact form fields, validation, spam, email contract
│   └── seo-accessibility.md # SEO metadata, sitemap, robots, a11y acceptance contract
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
manage.py
pyproject.toml                # ruff, mypy, pytest, coverage config
requirements.in               # top-level deps (human-edited)
requirements.txt              # compiled + pinned lockfile (pip-tools)
requirements-dev.in / .txt    # dev/test deps
.pre-commit-config.yaml
.github/workflows/ci.yml      # lint + typecheck + test + coverage gate

portfolio/                    # Django project package
├── settings/
│   ├── base.py               # shared settings, INSTALLED_APPS, Wagtail config
│   ├── dev.py                # SQLite, DEBUG, local email backend
│   └── prod.py               # PostgreSQL, security, WhiteNoise, CodeRed-required file
├── urls.py                   # Wagtail + Django admin + sitemap + robots + documents
└── wsgi.py                   # WSGI entrypoint (required by CodeRed)

core/                         # shared building blocks (no user-facing pages of its own)
├── models.py                 # SeoMixin / BasePage, StreamField blocks, SiteSettings
├── templates/core/           # base.html, partials (nav, footer, seo head, skip-link)
└── tests/

home/                         # HomePage, AboutPage (singleton-style landing + about)
├── models.py
├── templates/home/
└── tests/

projects/                     # ProjectIndexPage, ProjectPage
├── models.py
├── templates/projects/
└── tests/

blog/                         # BlogIndexPage, ArticlePage, ArticleTag
├── models.py
├── templates/blog/
└── tests/

contact/                      # ContactPage (Wagtail form), honeypot + time-trap, email
├── models.py
├── forms.py
├── templates/contact/
└── tests/

static/                       # source static assets (CSS, minimal progressive-enhancement JS, fonts)
templates/                    # project-wide template overrides (404.html, 500.html, sitemap)
```

**Structure Decision**: Single Django project (not split frontend/backend) because the site is
server-rendered with Django templates — there is no separate SPA. Content is organized into small,
single-responsibility Wagtail apps by page family (`home`, `projects`, `blog`, `contact`) plus a
`core` app holding shared mixins, StreamField blocks, and the base templates. This matches Wagtail
conventions, keeps each app independently testable (Principle II), and keeps model/query
responsibilities cohesive (Principle I).

## Complexity Tracking

> No constitution violations. No entries required.
