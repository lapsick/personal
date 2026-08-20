# Personal Professional Website

A server-rendered personal/professional website for a Software Engineer & Architect
(Microsoft/.NET focus), built with **Django 5.2** and **Wagtail 7.4**. Every page
(Home, About, Projects, Blog, Contact) is owner-editable through the Wagtail admin.
Core content and the contact path work without JavaScript (progressive enhancement),
targeting WCAG 2.1 AA, good Core Web Vitals, and privacy-compliant contact handling.

## Tech stack

- Python 3.12, Django 5.2 LTS, Wagtail 7.4 LTS
- PostgreSQL in production (CodeRed Cloud), SQLite locally
- [Pico CSS](https://picocss.com) (v2, vendored as a static asset) for styling —
  classless/semantic-first with automatic light/dark theming via `prefers-color-scheme`;
  `static/css/main.css` is a thin project override layer on top
- WhiteNoise for static files; `pip-tools` for dependency locking
- Tooling: `ruff` (format + lint), `mypy` + `django-stubs`, `pytest` (+ `pytest-django`, `pytest-cov`)

## Local setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1   |   bash: source .venv/bin/activate
pip install -r requirements-dev.txt          # compiled from requirements-dev.in via pip-tools

python manage.py migrate                     # DJANGO_SETTINGS_MODULE defaults to portfolio.settings.dev
python manage.py seed_site                   # create the initial page tree (idempotent)
python manage.py createsuperuser
python manage.py runserver
```

- Site: <http://127.0.0.1:8000/>
- Wagtail admin: <http://127.0.0.1:8000/cms/>

In the admin, fill in `Settings → Site settings` (owner name, title, contact email,
profile links, resume document) and edit each page's content.

## Project layout

```text
portfolio/settings/{base,dev,prod}.py   # split settings (prod.py required by CodeRed Cloud)
core/     # BasePage/SEO mixin, StreamField blocks, SiteSettings, base templates, nav/footer/SEO partials
home/     # HomePage (site root) + AboutPage
projects/ # ProjectIndexPage + ProjectPage
blog/     # BlogIndexPage + ArticlePage (+ tags)
contact/  # ContactPage (Wagtail form) with honeypot + time-trap spam protection
static/   # source CSS (css/vendor/pico.min.css + css/main.css override layer)
templates/# project-wide 404/500
```

## Quality gates

Run before every PR (also enforced in CI, `.github/workflows/ci.yml`):

```bash
ruff format --check .
ruff check .
mypy .
pytest -m "not integration"                                  # isolated unit tests
pytest -m integration --cov-append --cov-fail-under=80        # DB/email/HTTP flows + combined coverage gate
pre-commit run --all-files
```

Coverage is enforced at **≥ 80%** on the combined unit + integration run. Accessibility
is checked in CI with `pa11y-ci` (axe, WCAG 2.1 AA) across the six key pages
(`.pa11yci.json`).

## Privacy / data retention

Contact submissions are stored minimally (name, reply-to email, message) and the
message body is never written to logs. Prune stored submissions past the retention
window (default 365 days, `CONTACT_SUBMISSION_RETENTION_DAYS`):

```bash
python manage.py prune_contact_submissions            # or --days N / --dry-run
```

Schedule this daily in production.

## Deploy to CodeRed Cloud (free tier)

CodeRed Cloud provides managed Django/Wagtail on Azure with automatic HTTPS,
PostgreSQL, and daily backups. It requires `portfolio/settings/prod.py` and
`portfolio/wsgi.py` (both present).

```bash
pip install cr
cr login
cr check <webapp-handle>     # scans the project, offers to fix settings/prod.py for the platform
cr deploy <webapp-handle>    # deploys; provisions PostgreSQL, serves static/media, issues HTTPS
```

Production reads all secrets/host values from environment variables (nothing secret in
source): `SECRET_KEY`, `ALLOWED_HOSTS`, `WAGTAILADMIN_BASE_URL`, `DB_*`, `EMAIL_*`,
`CSRF_TRUSTED_ORIGINS`. After deploy: run `migrate`, create the admin user, run
`seed_site` (or publish pages manually), and verify HTTPS.

Post-deploy production checklist:

- `python manage.py check --deploy` reports no critical issues
- `DEBUG=False`; `SECRET_KEY` and `ALLOWED_HOSTS` come from the environment
- PostgreSQL connected; static and media served; resume document downloads
- `/sitemap.xml` and `/robots.txt` reachable; contact form notifies the owner
