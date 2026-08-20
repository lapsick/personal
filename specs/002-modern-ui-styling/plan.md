# Implementation Plan: Modern UI Restyle (Pico CSS)

**Branch**: `002-modern-ui-styling` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-modern-ui-styling/spec.md`

## Summary

Restyle the public-facing site with **Pico CSS**, a lightweight classless/semantic-first
framework with built-in light/dark theming. Approach: vendor Pico's minified stylesheet as a
static asset loaded *before* a slimmed-down `main.css`, which is reduced to a thin project layer
holding only the bits Pico does not cover (skip link, honeypot, card grid, nav active indicator,
tag list, visually-hidden helper, error/summary emphasis). Templates already use semantic markup
(`<header>`, `<nav>`, `<article>`, `<form>`, native `<button>`), so Pico styles most of the page
automatically; template edits are minimal and confined to aligning a few custom hooks with Pico's
conventions. Dark mode is delivered by Pico's `prefers-color-scheme` support — no JavaScript, no
theme toggle — satisfying the "follow system preference" requirement while preserving the site's
no-JS, accessibility, and performance guarantees.

## Technical Context

**Language/Version**: Python 3.12 (server-side templates only; no Python logic change)

**Primary Dependencies**: Django 5.2, Wagtail 7.4 (existing). New front-end dependency: **Pico CSS**
(vendored static stylesheet, no package-manager/Node build step)

**Storage**: N/A — presentation-only change; no models, migrations, or CMS field changes

**Testing**: pytest (unit + integration markers), pa11y-ci (`axe`, WCAG2AA) for accessibility

**Target Platform**: Server-rendered web (Django templates), evergreen browsers + mobile viewports

**Project Type**: Web application — single Django project with per-app Wagtail modules

**Performance Goals**: No render-blocking heavyweight assets; total added CSS weight small
(Pico min ≈ 80KB raw / ≈10KB gzipped) and served as a cacheable static file; FCP and page weight
must not regress > 10% vs. pre-restyle baseline (SC-007)

**Constraints**: WCAG 2.1 AA contrast in light **and** dark (FR-006); no horizontal scroll at 360px
(SC-005); contact form fully functional with JavaScript disabled (FR-009); no new a11y violations
(FR-010); `class="skip-link"` markup preserved (asserted by existing tests)

**Scale/Scope**: 7 audited pages / page types; 5 StreamField block templates; 2 shared partials
(nav, footer); base template; ~314-line `main.css` reduced to a thin override layer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Assessment | Status |
|-----------|------------|--------|
| I. Code Quality | No new Python modules; template edits keep single responsibility; CSS layered (vendor + thin project layer) with clear separation. `ruff`/`mypy` scope unchanged. | PASS |
| II. Testing Standards (NON-NEGOTIABLE) | Add/extend rendering tests (Pico stylesheet linked, skip-link preserved, block templates render). Existing suites must stay green; combined coverage ≥ 80% maintained. No coverage decrease. | PASS |
| III. UX Consistency | Feature's entire purpose is one consistent style across all surfaces; existing structured/human output modes unaffected; no breaking interface changes. | PASS |
| IV. Performance Requirements | Vendored, cacheable CSS; no JS added; no new render-blocking third-party requests. Existing query-count performance tests unaffected. FCP/weight budget in SC-007. | PASS |
| Python Environment Standards | **No new Python dependency** (Pico is a static asset), so lockfile/venv posture is unchanged. | PASS |
| Workflow & Quality Gates | Change ships via PR with CI (lint, type-check, tests, pa11y) as today. | PASS |

**Result**: PASS — no violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/002-modern-ui-styling/
├── plan.md              # This file (/speckit-plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── ui-contract.md   # Visual/interaction contract for the restyle
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created here)
```

### Source Code (repository root)

```text
static/
└── css/
    ├── vendor/
    │   └── pico.min.css        # NEW — vendored Pico CSS (pinned version)
    └── main.css                # REDUCED — thin project override layer over Pico

core/templates/core/
├── base.html                   # EDIT — link pico.min.css before main.css; set color-scheme
├── partials/
│   ├── nav.html                # EDIT (minimal) — align with Pico <nav> conventions
│   └── footer.html             # EDIT (minimal) — align footer styling hooks
└── blocks/
    ├── code_block.html         # VERIFY/EDIT — code/pre styling under Pico
    ├── heading_block.html      # VERIFY
    ├── image_block.html        # VERIFY — figure/caption under Pico
    ├── paragraph_block.html    # VERIFY
    └── quote_block.html        # VERIFY — blockquote under Pico

home/templates/home/           # EDIT (minimal) — hero/cards align with Pico
projects/templates/projects/   # EDIT (minimal) — index cards + detail
blog/templates/blog/           # EDIT (minimal) — index list + article
contact/templates/contact/     # EDIT (minimal) — form controls, error/summary, buttons
templates/{404,500}.html       # VERIFY — error pages under Pico

core/tests/test_rendering.py   # EDIT — assert Pico linked + skip-link preserved + blocks render
.pa11yci.json                  # UNCHANGED — same audited URLs; re-run as acceptance gate
```

**Structure Decision**: Single Django project (Option 1 / web application variant). The restyle
touches only the presentation layer — the vendored stylesheet under `static/css/vendor/`, the
reduced `static/css/main.css`, the shared base template + partials, per-app page templates, the
StreamField block templates, and the rendering test module. No new app, model, or migration.

## Complexity Tracking

> No Constitution Check violations — section intentionally empty.
