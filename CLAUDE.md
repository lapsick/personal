# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

Server-rendered personal/professional website built with **Django 5.2** + **Wagtail 7.4**
on **Python 3.12**. Content (Home, About, Projects, Blog, Contact) is owner-editable through
the Wagtail admin. See `README.md` for full setup and deployment; feature specs live under
`specs/001-personal-website/`.

### Architecture

Single Django project (`portfolio/`) with small, single-responsibility Wagtail apps:

- `core/` — `BasePage`/SEO mixin, curated StreamField blocks, `SiteSettings`, base
  templates, and the nav/footer/SEO partials (via `core.context_processors.site_settings`
  and `core.templatetags.navigation_tags`). Also holds `seed_site` and utility views.
- `home/` — `HomePage` (site root) and `AboutPage`.
- `projects/` — `ProjectIndexPage` + `ProjectPage`.
- `blog/` — `BlogIndexPage` + `ArticlePage` (taggit tags).
- `contact/` — `ContactPage` (Wagtail `AbstractEmailForm`) with no-JS honeypot + time-trap
  spam protection (`contact/forms.py`), reply-to email notification, and send-failure fallback.

Split settings: `portfolio/settings/{base,dev,prod}.py` (`DJANGO_SETTINGS_MODULE` defaults to
`portfolio.settings.dev`; `prod.py` is required by CodeRed Cloud).

### Common commands

```bash
python manage.py migrate            # apply migrations (SQLite locally)
python manage.py seed_site          # create the initial page tree (idempotent)
python manage.py runserver          # site at /, Wagtail admin at /cms/

ruff format . && ruff check . && mypy .    # format, lint, type-check
pytest -m "not integration"                                # isolated unit tests
pytest -m integration --cov-append --cov-fail-under=80     # flows + combined 80% coverage gate
pytest path/to/test_file.py::test_name --no-cov            # run a single test
```

Coverage is enforced at ≥ 80% on the combined unit + integration run (not unit-only), since
much of the code is view/template-driven. Accessibility runs in CI via `pa11y-ci` (`.pa11yci.json`).

## Project constitution

Non-negotiable project principles (code quality, testing standards, UX consistency, performance
requirements, Python environment standards, and workflow/quality gates) are defined in
`.specify/memory/constitution.md`. Read it before making changes and ensure all work complies.
