---
description: "Task list for Personal Professional Website implementation"
---

# Tasks: Personal Professional Website

**Input**: Design documents from `specs/001-personal-website/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED. The project constitution (`.specify/memory/constitution.md`) makes automated
`pytest` testing NON-NEGOTIABLE (Principle II: happy + edge/error paths, isolated units, tagged
integration, ≥80% coverage). Test tasks are therefore mandatory, not optional, for this feature.

**Organization**: Tasks are grouped by user story (from spec.md) so each story is an independently
implementable and testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 (P1), US2 (P2), US3 (P3); Setup/Foundational/Polish carry no story label
- Exact file paths are included in each task

## Project layout (from plan.md)

Single Django project at repo root: `portfolio/` (project package) + Wagtail apps `core/`, `home/`,
`projects/`, `blog/`, `contact/`; source `static/` and project `templates/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and quality tooling.

- [ ] T001 Create Django project skeleton at repo root: `manage.py` and `portfolio/` package (`portfolio/__init__.py`, `portfolio/wsgi.py`), targeting Python 3.12
- [ ] T002 Author `requirements.in` (Django 5.2, wagtail 7.4, `psycopg[binary]`, whitenoise) and `requirements-dev.in` (pytest, pytest-django, pytest-cov, factory_boy, ruff, mypy, django-stubs, pre-commit, pip-tools), then compile pinned `requirements.txt` and `requirements-dev.txt` via `pip-compile`
- [ ] T003 [P] Configure `pyproject.toml` with ruff (format + lint), mypy + django-stubs, and pytest/coverage settings (`DJANGO_SETTINGS_MODULE=portfolio.settings.dev`, markers incl. `integration`, `--cov-fail-under=80`)
- [ ] T004 [P] Create `.pre-commit-config.yaml` running ruff-format, ruff, and mypy
- [ ] T005 [P] Create `.github/workflows/ci.yml` running lint → typecheck → `pytest -m "not integration"` (coverage gate) → `pytest -m integration`, pinned to Python 3.12

**Checkpoint**: `pip install -r requirements-dev.txt` succeeds and tooling runs.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wagtail project config, the `core` app (base templates, SEO, nav, settings), and
site-wide infrastructure every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Create split settings `portfolio/settings/{__init__,base,dev,prod}.py`: `base` (INSTALLED_APPS incl. wagtail + apps, Wagtail config, WhiteNoise middleware + `CompressedManifestStaticFilesStorage`, `<html lang>`/i18n), `dev` (SQLite, DEBUG=True, console email backend), `prod` (PostgreSQL via env vars, DEBUG=False, `SECRET_KEY`/`ALLOWED_HOSTS` from env, HTTPS/security headers) — CodeRed-required `prod.py` name
- [ ] T007 Configure `portfolio/urls.py`: Wagtail admin (`/cms/`), Django admin, Wagtail document serving, `search`/pages, and mount points for sitemap + robots; confirm `portfolio/wsgi.py` entrypoint
- [ ] T008 Create `core` app (`core/__init__.py`, `core/apps.py`) and register it in `INSTALLED_APPS`
- [ ] T009 [P] Implement `BasePage`/`SeoMixin` abstract page in `core/models.py` (fields: `social_image`, `canonical_url`; inherits Wagtail `seo_title`/`search_description`) per data-model.md
- [ ] T010 [P] Implement the curated StreamField block set (`heading`, `paragraph`, `code`, `image`, `quote`; no raw HTML) in `core/blocks.py`
- [ ] T011 [P] Implement `SiteSettings` Wagtail settings model in `core/models.py` (owner_name, professional_title, tagline, resume_document, contact_email, linkedin_url, github_url, other_profiles) with email-obfuscation rendering per FR-025
- [ ] T012 Create base layout `core/templates/core/base.html` with semantic landmarks (`header`/`nav`/`main`/`footer`), a visible-on-focus skip-to-content link, and `<html lang>`
- [ ] T013 [P] Create navigation + footer partials `core/templates/core/partials/{nav,footer}.html` rendering all five sections with a current-page indicator (FR-002/003), pulling profile links from `SiteSettings`
- [ ] T014 [P] Create SEO head partial `core/templates/core/partials/seo_head.html` emitting `<title>`, meta description, canonical, and Open Graph/Twitter tags per contracts/seo-accessibility.md
- [ ] T015 [P] Create branded, accessible `templates/404.html` and `templates/500.html` with full navigation
- [ ] T016 Implement `/sitemap.xml` (`wagtail.contrib.sitemaps`) and `/robots.txt` (references sitemap, disallows admin) wired in `portfolio/urls.py`
- [ ] T017 [P] Create mobile-first responsive CSS scaffold with AA-contrast design tokens and visible focus styles in `static/css/main.css`; wire into `base.html`
- [ ] T018 [P] Add shared test scaffolding: `conftest.py` (pytest-django + Wagtail root-page fixtures) and `core/tests/factories.py` (factory_boy base factories)
- [ ] T019 Run initial migrations and verify the Wagtail admin loads with `SiteSettings` editable (`python manage.py migrate` on dev/SQLite)

**Checkpoint**: Wagtail admin runs, base layout + nav + SEO head + sitemap/robots + error pages
exist, and shared test fixtures are in place. User stories can now begin.

---

## Phase 3: User Story 1 - Recruiter/CTO lands and reaches out (Priority: P1) 🎯 MVP

**Goal**: A visitor understands who the owner is within seconds on the home page and can reach a
working contact path in one click, with a validated, spam-protected, no-JS contact form.

**Independent Test**: Load `/` cold — owner name/title/.NET specialization visible above the fold;
the contact CTA reaches `/contact/` in one click; submitting a valid message (JS disabled) shows a
confirmation and notifies the owner; invalid input and spam are handled per contract.

### Tests for User Story 1

- [ ] T020 [P] [US1] Unit tests for `HomePage` required fields (hero, CTA target) in `home/tests/test_models.py`
- [ ] T021 [P] [US1] Unit tests for contact form validation, honeypot rejection, and time-trap rejection in `contact/tests/test_forms.py`
- [ ] T022 [P] [US1] Integration test (`@pytest.mark.integration`) for `POST /contact/`: valid submit → email queued + confirmation rendered; forced send failure → fallback channels shown, in `contact/tests/test_contact_flow.py`

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create `home` app and `HomePage(BasePage)` model in `home/models.py` (hero_heading, hero_subheading, primary_cta_label, primary_cta_page, intro StreamField, optional featured_projects/featured_articles) per data-model.md
- [ ] T024 [P] [US1] Create `contact` app and `ContactPage(AbstractEmailForm)` in `contact/models.py` with intro/thank_you_text/to_address, plus honeypot + signed `form_rendered_at` fields and validation logic in `contact/forms.py` per contracts/contact-form.md
- [ ] T025 [US1] Implement HomePage template `home/templates/home/home_page.html`: name/title/specialization above the fold, prominent contact CTA, featured previews (graceful when empty) — FR-005/006/007
- [ ] T026 [US1] Implement ContactPage template `contact/templates/contact/contact_page.html`: labeled fields, `aria-describedby` error association + error summary, hidden honeypot (`aria-hidden`), privacy notice, and fallback channels from `SiteSettings` — FR-015/016/018
- [ ] T027 [US1] Implement submission processing in `contact/models.py`: spam drop (honeypot/time-trap, silent), owner email notification with sender reply-to, on-page confirmation, and send-failure fallback — FR-017/018/019
- [ ] T028 [US1] Add SEO metadata for Home and Contact (via SEO head partial) and confirm nav current-page indicator on both routes
- [ ] T029 [US1] Verify keyboard-only operation + no-JS submission for Home and Contact; run axe-core against both (zero critical/serious) — FR-022, SC-004

**Checkpoint**: MVP — Home + Contact fully functional, accessible, and independently testable.

---

## Phase 4: User Story 2 - Credibility via work & background (Priority: P2)

**Goal**: A visitor can read the owner's background/expertise on About and browse concrete work
examples on Projects with enough context to judge relevance, plus download the resume.

**Independent Test**: `/about/` shows background, expertise, engagement types, and a working resume
download; `/projects/` lists projects (graceful empty state when none) and each project shows
problem/role/approach/technologies/outcome with external links opening safely in a new tab.

### Tests for User Story 2

- [ ] T030 [P] [US2] Unit tests for `AboutPage`, `ProjectIndexPage`, and `ProjectPage` fields/validation (incl. external-link URL validation) in `projects/tests/test_models.py`
- [ ] T031 [P] [US2] Integration test (`@pytest.mark.integration`) for projects index: empty-state renders 200, listing shows cards, and external links carry `rel="noopener noreferrer"`, in `projects/tests/test_projects_flow.py`

### Implementation for User Story 2

- [ ] T032 [P] [US2] Create `AboutPage(BasePage)` model in `home/models.py` (intro, body StreamField, expertise_areas, engagement_types, resume CTA from `SiteSettings.resume_document`) per data-model.md
- [ ] T033 [P] [US2] Create `projects` app with `ProjectIndexPage(BasePage)` and `ProjectPage(BasePage)` in `projects/models.py` (summary, problem, role, approach, technologies, outcome, external_links, featured_image, date)
- [ ] T034 [US2] Implement AboutPage template `home/templates/home/about_page.html` (background, expertise, engagement types, resume download link) — FR-008
- [ ] T035 [US2] Implement ProjectIndexPage template `projects/templates/projects/project_index_page.html` (cards with title/summary/technologies + graceful empty state) — FR-009/011
- [ ] T036 [US2] Implement ProjectPage template `projects/templates/projects/project_page.html` (problem/role/approach/technologies/outcome, external links with `target=_blank rel=noopener`) — FR-009/010
- [ ] T037 [US2] Add SEO metadata for About/Projects pages and wire resume Wagtail Document download from `SiteSettings`
- [ ] T038 [US2] Verify accessibility + responsive (320–1920px) for About and Projects; run axe-core (zero critical/serious) — FR-021/022

**Checkpoint**: US1 and US2 both work independently.

---

## Phase 5: User Story 3 - Technical writing & reputation (Priority: P3)

**Goal**: A visitor can browse the article list and read individual articles (directly linkable and
shareable), building trust in the owner's .NET architecture expertise.

**Independent Test**: `/blog/` lists articles (title, date, summary) most-recent-first with a
graceful empty state; opening an article by its own URL renders full content plus navigation.

### Tests for User Story 3

- [ ] T039 [P] [US3] Unit tests for `BlogIndexPage`, `ArticlePage`, `ArticleTag`, and date-desc ordering in `blog/tests/test_models.py`
- [ ] T040 [P] [US3] Integration test (`@pytest.mark.integration`) for blog: index ordering + empty-state, and direct article-URL entry renders full nav, in `blog/tests/test_blog_flow.py`

### Implementation for User Story 3

- [ ] T041 [P] [US3] Create `blog` app with `BlogIndexPage(BasePage)`, `ArticlePage(BasePage)`, and `ArticleTag` (taggit through-model) in `blog/models.py` (title, date, summary, body StreamField, tags, featured_image)
- [ ] T042 [US3] Implement BlogIndexPage template `blog/templates/blog/blog_index_page.html` (title/date/summary list, most-recent first, graceful empty state) — FR-012/014
- [ ] T043 [US3] Implement ArticlePage template `blog/templates/blog/article_page.html` (full article: title/date/body, shareable, full nav on direct entry) — FR-013
- [ ] T044 [US3] Add per-article SEO + social card metadata (`og:image` from featured_image) and wire `HomePage.featured_articles` previews — FR-007/023, SC-008
- [ ] T045 [US3] Verify accessibility + responsive for blog index and article; run axe-core (zero critical/serious) — FR-021/022

**Checkpoint**: All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Site-wide gates spanning all stories.

- [ ] T046 [P] Add sitemap/robots coverage test asserting all five page types + every published article appear in `/sitemap.xml` and admin is disallowed — FR-023, SC-009
- [ ] T047 [P] Performance pass: Wagtail responsive image renditions with explicit width/height (CLS), template-fragment caching for nav/index pages, and `select_related`/`prefetch_related`; add per-page-type DB query-budget assertions (no N+1) in `*/tests/test_performance.py` — SC-005, Principle IV
- [ ] T048 [P] Privacy pass: contact-submission retention policy, exclude message body from logs, and confirm privacy notice renders adjacent to the form — FR-025/D11
- [ ] T049 [P] Run axe-core/pa11y in CI across the six key pages (Home, About, Projects index+detail, Blog index+article, Contact); fix any critical/serious violations — SC-004
- [ ] T050 [P] Author `README.md` (local setup + quality gates) and deploy notes for CodeRed Cloud (`cr install/login/check/deploy`, `settings/prod.py`, env secrets, HTTPS, daily backups); update root `CLAUDE.md` repository-status section
- [ ] T051 Production config validation: run `cr check <webapp>`, confirm `DEBUG=False`, env-provided `SECRET_KEY`/`ALLOWED_HOSTS`, PostgreSQL connectivity, and static/media serving
- [ ] T052 Execute quickstart.md V1–V7 validation end-to-end and confirm coverage ≥80% and all gates green

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — **blocks all user stories**.
- **User Stories (Phase 3–5)**: each depends only on Foundational; independent of each other and may
  proceed in parallel. Priority order for sequential delivery: US1 → US2 → US3.
- **Polish (Phase 6)**: depends on the user stories it touches (T046/T047/T049 span all three).

### Story-level notes

- **US1 (P1)**: fully independent. `HomePage.featured_projects/articles` are optional and render
  empty until US2/US3 exist, so US1 remains independently testable.
- **US2 (P2)**: independent; enriches Home featured previews additively (no US1 changes required).
- **US3 (P3)**: independent; wires `HomePage.featured_articles` additively in T044.

### Within each story

- Tests (T020–T022, T030–T031, T039–T040) are written first and must fail before implementation.
- Models before templates; templates before submission/SEO wiring; accessibility verification last.

### Parallel opportunities

- Setup: T003, T004, T005 in parallel.
- Foundational: T009, T010, T011 in parallel; then T013, T014, T015, T017, T018 in parallel.
- Each story's test tasks marked [P] run together; model tasks marked [P] run together.
- With capacity, US1/US2/US3 can be built by different developers once Phase 2 is done.
- Polish: T046, T047, T048, T049, T050 in parallel.

---

## Parallel Example: User Story 1

```bash
# Tests for US1 (write first, expect failure):
Task: "Unit tests for HomePage fields in home/tests/test_models.py"            # T020
Task: "Unit tests for contact form/honeypot/time-trap in contact/tests/test_forms.py"  # T021
Task: "Integration test for POST /contact/ in contact/tests/test_contact_flow.py"      # T022

# Then models in parallel:
Task: "Create HomePage model in home/models.py"          # T023
Task: "Create ContactPage + forms in contact/models.py"  # T024
```

---

## Implementation Strategy

### MVP first (User Story 1 only)

1. Phase 1 Setup → 2. Phase 2 Foundational (CRITICAL) → 3. Phase 3 US1 → **STOP & validate** Home +
Contact independently (quickstart V1, V4) → deploy/demo if ready.

### Incremental delivery

Setup + Foundational → US1 (MVP, deploy) → US2 (deploy) → US3 (deploy) → Polish. Each story adds
value without breaking prior stories.

### Parallel team strategy

After Phase 2: Developer A → US1, Developer B → US2, Developer C → US3; integrate independently.

---

## Notes

- [P] = different files, no incomplete-task dependencies.
- Tests are mandatory here (Constitution II); verify they fail before implementing.
- Keep ≥80% coverage, non-decreasing; unit tests isolated (no network), integration tagged.
- Commit after each task or logical group; stop at any checkpoint to validate a story independently.
- Hosting/framework specifics stay in plan/tasks, never in the spec.
