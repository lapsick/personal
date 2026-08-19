# Quickstart & Validation Guide: Personal Professional Website

**Feature**: 001-personal-website | **Date**: 2026-08-18

A run/validation guide proving the feature works end-to-end. Implementation details (model bodies,
migrations, full test suites) live in `tasks.md` and the implementation phase, not here.

## Prerequisites

- Python 3.12 and a virtual environment tool
- Git (feature branch `001-personal-website` already checked out)
- No database server needed locally (SQLite); PostgreSQL is used only in production (CodeRed Cloud)

## Local setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1   |   bash: source .venv/bin/activate
pip install -r requirements-dev.txt        # compiled from requirements-dev.in via pip-tools
python manage.py migrate                   # DJANGO_SETTINGS_MODULE=portfolio.settings.dev
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` (site) and `http://127.0.0.1:8000/cms/` (Wagtail admin).

**First-run content**: in Wagtail admin, publish the HomePage, AboutPage, ProjectIndexPage,
BlogIndexPage, and ContactPage, and fill `SiteSettings` (owner name, title, contact email, profile
links, resume document). This proves FR-024 (owner edits all content with no code changes).

## Validation scenarios (map to spec Success Criteria & FRs)

Each scenario is runnable/observable; automated equivalents are noted (see plan D10).

### V1 — Identity & one-click contact (SC-001, SC-002; FR-005/006)
1. Load `/`. Confirm owner name, title (Software Engineer & Architect), and .NET/Microsoft
   specialization are visible without scrolling.
2. Confirm a prominent contact CTA reaches `/contact/` in one click.

### V2 — Credibility via work & about (US2; FR-008/009/010)
1. `/about/` shows background, expertise, engagement types, and a resume download link.
2. `/projects/` lists projects; open one and confirm problem/role/approach/technologies/outcome and
   external links opening in a new tab with `rel=noopener`.

### V3 — Technical writing (US3; FR-012/013/014)
1. `/blog/` lists articles (title, date, summary), most-recent first.
2. Open an article directly by its URL; confirm full content + working nav (shareable, self-orienting).
3. With no articles/projects published, confirm `/blog/` and `/projects/` show graceful empty states.

### V4 — Contact form, validation, spam, no-JS (FR-015..019; SC-003)
Reference: [contracts/contact-form.md](./contracts/contact-form.md).
1. **No-JS**: disable JavaScript; submit a valid message; confirm on-page confirmation and that the
   owner notification email is produced (console email backend in dev prints it).
2. **Validation**: submit with a missing/invalid email; confirm a field-level error naming the field.
3. **Honeypot**: fill the hidden honeypot field and submit; confirm nothing is emailed/persisted.
4. **Time-trap**: submit within the sub-threshold window; confirm rejection as spam.
5. **Failure fallback**: simulate email send failure; confirm the error + fallback channels (email,
   LinkedIn/GitHub) render (FR-018).

### V5 — SEO, sitemap, social (FR-023; SC-008/009)
Reference: [contracts/seo-accessibility.md](./contracts/seo-accessibility.md).
1. `GET /sitemap.xml` lists all five page types + every published article.
2. `GET /robots.txt` references the sitemap and disallows admin.
3. View source on `/` and an article: confirm `<title>`, meta description, canonical, and OG/Twitter
   tags with an image.

### V6 — Accessibility & responsive (FR-021/022; SC-004/006)
1. Keyboard-only: tab through nav → main → contact form → submit; confirm skip link + visible focus.
2. Run axe-core/pa11y against the six key pages; confirm zero critical/serious violations.
3. Resize 320px → 1920px; confirm no horizontal scroll/overflow on any page type.

### V7 — Performance (SC-005; Principle IV)
1. Lighthouse/CWV lab run on Home, an index page, and an article meets LCP ≤ 2.5s, CLS ≤ 0.1,
   INP ≤ 200ms (mobile profile).
2. Test asserts per-page-type DB query counts stay within budget (no N+1 on index pages).

## Quality gates (run before every PR — Constitution)

```bash
ruff format --check .
ruff check .
mypy .
pytest -m "not integration" --cov --cov-fail-under=80   # isolated unit tests
pytest -m integration                                    # DB/email/routing flows
pre-commit run --all-files
```

CI (`.github/workflows/ci.yml`) runs the same lint + typecheck + unit + integration + coverage gate;
a failing run blocks merge (Development Workflow & Quality Gates).

## Deploy to CodeRed Cloud (free tier)

Reference: research D3. Hosting/framework details are confined to the plan, not the spec.

```bash
pip install cr
cr login
cr check <webapp-handle>     # scans project, offers to fix settings/prod.py for the platform
cr deploy <webapp-handle>    # deploys; platform provisions PostgreSQL, serves static/media,
                             # issues HTTPS certificate, and enables daily backups
```

Post-deploy: run migrations + create the admin user (per CodeRed dashboard/CLI), publish pages, and
verify HTTPS. Confirm the production checklist: `DEBUG=False`, `ALLOWED_HOSTS` from env, `SECRET_KEY`
from env (platform-cycled), PostgreSQL connected, resume document downloads, sitemap reachable.

## Success definition

The feature is validated when V1–V7 pass, the quality gates are green at ≥80% coverage, and the
production deployment serves all five pages over HTTPS with the contact form notifying the owner.
