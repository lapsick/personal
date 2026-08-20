---
description: "Task list for Modern UI Restyle (Pico CSS)"
---

# Tasks: Modern UI Restyle (Pico CSS)

**Input**: Design documents from `/specs/002-modern-ui-styling/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contract.md, quickstart.md

**Tests**: Test/verification tasks ARE included — Constitution Principle II (Testing Standards) is
NON-NEGOTIABLE and the spec's success criteria depend on pytest + `pa11y-ci`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task serves (US1, US2, US3)
- All paths are repository-relative.

## Path notes

Single Django project. Styling lives in `static/css/`; templates in `<app>/templates/` and
`core/templates/core/`; rendering tests in `core/tests/test_rendering.py`; accessibility config in
`.pa11yci.json`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Vendor the framework and capture the regression baseline.

- [X] T001 Create `static/css/vendor/` and add a pinned `static/css/vendor/pico.min.css` (record the exact Pico version in a header comment), sourced from the MIT-licensed Pico release (research D1, D7)
- [X] T002 [P] Capture the pre-restyle baseline into `specs/002-modern-ui-styling/baseline.md`: current `pa11y-ci` result summary for all `.pa11yci.json` URLs, plus FCP and total page weight for `/blog/sample-article/` (baseline for SC-004 and SC-007)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire Pico into the base template and reduce `main.css` to an override-layer scaffold.

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete (both edits touch
shared shell files every page depends on).

- [X] T003 In `core/templates/core/base.html`, add `<link>` to `css/vendor/pico.min.css` **before** the existing `css/main.css` link, and declare dual color-scheme support (e.g. `<meta name="color-scheme" content="light dark">`) so native controls theme correctly (contract C1; research D3, D4)
- [X] T004 Reduce `static/css/main.css` to a thin override-layer scaffold: KEEP `.skip-link`, `:focus-visible`, `.hp-field`, `.visually-hidden`, and `.container`; REMOVE base rules now provided by Pico (base typography, `a` color, generic form-control styling, `.button` base, `main` measure, base `img`); re-express any retained custom colors using Pico `--pico-*` variables so they adapt to both themes (research D3, D5)

**Checkpoint**: Every page now loads Pico + the reduced override layer; story work can begin.

---

## Phase 3: User Story 1 - Cohesive modern look across all pages (Priority: P1) 🎯 MVP

**Goal**: Every page (Home, About, Projects index/detail, Blog index/article, Contact) and every
StreamField block presents one consistent, modern Pico style — nothing unstyled or broken.

**Independent Test**: Load all 7 audited URLs and confirm shared typography/spacing/nav/footer and
that each block type (heading, paragraph, code, image, quote) renders cleanly (SC-001, SC-002).

### Tests for User Story 1

- [X] T005 [P] [US1] In `core/tests/test_rendering.py`, assert `base.html` output links `css/vendor/pico.min.css` and that it appears **before** `css/main.css`, and that `class="skip-link"` is still present (contract C1; guards the existing skip-link assertion)
- [X] T006 [P] [US1] In `core/tests/test_rendering.py`, add a test that a page whose body StreamField contains all five block types (heading, paragraph, code, image, quote) renders 200 with each block's wrapper present and no template error (contract C3, SC-002)

### Implementation for User Story 1

- [X] T007 [P] [US1] Restyle `core/templates/core/partials/nav.html` to Pico's `<nav>` conventions while preserving the `.is-current` / `aria-current="page"` active indicator (contract C2)
- [X] T008 [P] [US1] Adjust `core/templates/core/partials/footer.html` styling hooks so the footer identity/links/copyright render cohesively under Pico (contract C2)
- [X] T009 [P] [US1] Verify/adjust the five block templates under `core/templates/core/blocks/` (`heading_block.html`, `paragraph_block.html`, `code_block.html`, `image_block.html`, `quote_block.html`) so `pre`/`figure`/`blockquote`/caption render correctly under Pico (contract C3)
- [X] T010 [US1] Add card-grid + card overrides to `static/css/main.css` for Home/Projects/Blog listings (`.card-grid`, `.card`, `.card__meta`, `.empty-state`) (contract C4)
- [X] T011 [US1] Add tag-list and article-list overrides to `static/css/main.css` (`.tag-list`, `.tag`, `.article-list`, `.article-list__item`, `.article__meta`) (contract C4)
- [X] T012 [US1] Align CTA buttons in `static/css/main.css`: style `.button` / `.button--secondary` anchors to match Pico's button look (or add `role="button"` in the templates that use them, e.g. `home/templates/home/home_page.html`) (contract C5; research D6)
- [X] T013 [US1] Visually verify page templates render cohesively and fix any per-page gaps: `home/templates/home/home_page.html`, `home/templates/home/about_page.html`, `projects/templates/projects/project_index_page.html`, `projects/templates/projects/project_page.html`, `blog/templates/blog/blog_index_page.html`, `blog/templates/blog/article_page.html`, and `templates/404.html` + `templates/500.html` (contract C4, SC-001, SC-008)

**Checkpoint**: All pages share one modern Pico style; MVP is demoable.

---

## Phase 4: User Story 2 - Light and dark appearance (Priority: P2)

**Goal**: The site renders a first-class dark theme under a dark OS preference and the light theme
otherwise, both AA-contrast, with no JavaScript toggle (research D4).

**Independent Test**: Toggle OS/browser to dark then light and reload each page; confirm coherent
themes and legible text in both (SC-003).

### Tests for User Story 2

- [X] T014 [P] [US2] In `core/tests/test_rendering.py`, assert the document declares dual color-scheme support (the `color-scheme` meta/attribute from T003 is present in rendered `base.html`) (contract C1, FR-005)

### Implementation for User Story 2

- [X] T015 [US2] Ensure every color in the `static/css/main.css` override layer (cards, tags, article meta, error/summary emphasis, honeypot-adjacent styling) is expressed via Pico `--pico-*` variables or theme-aware values so it adapts to dark mode; add dark-mode-specific overrides only where a custom rule doesn't already adapt (FR-006, contract C6)
- [X] T016 [US2] Manually verify all 7 audited pages in both dark and light per quickstart scenario 2, correcting any override that drops below WCAG 2.1 AA contrast in either theme (SC-003, FR-006)

**Checkpoint**: Both themes work automatically on every page.

---

## Phase 5: User Story 3 - Accessible, responsive, and fast after restyle (Priority: P2)

**Goal**: No regression in accessibility, responsiveness, performance, or the no-JS contact form.

**Independent Test**: Run `pa11y-ci`, keyboard-navigate, resize to 360px, and submit the contact
form with JS disabled — all pass against the pre-restyle baseline (SC-004, SC-005, SC-006, SC-007).

### Implementation for User Story 3

- [X] T017 [P] [US3] Confirm the `:focus-visible` outline retained in `static/css/main.css` is at least as visible/AA as before (or Pico's default meets the bar); adjust if weaker (contract C8, FR-008)
- [X] T018 [US3] Restyle the contact form under Pico in `contact/templates/contact/contact_page.html` + `static/css/main.css`: form controls, labels, required markers, per-field `.field-error`, `.error-summary`, `.form-field--error`, and the send-failure fallback — legible in both themes; keep `.hp-field` honeypot visually hidden/off-screen (contract C6, FR-009)
- [X] T019 [US3] Verify the contact form still submits and enforces spam protection with JavaScript disabled (no-JS path intact), including `contact/templates/contact/contact_page_landing.html` success state (SC-006, FR-009)
- [X] T020 [US3] Responsive pass at 360px for all 7 pages: ensure `pre`/`code`, wide tables, and images scroll within their own container and the page body has no horizontal overflow; add container overrides to `static/css/main.css` if needed (contract C7, SC-005)
- [ ] T021 [P] [US3] Run `npx pa11y-ci` (uses `.pa11yci.json`) and confirm **zero new violations** vs `specs/002-modern-ui-styling/baseline.md` (SC-004, FR-010, contract C8) — DEFERRED TO CI: `pa11y-ci` + headless Chrome are not installed locally. Structural a11y (skip link, landmarks, labelled fields, honeypot, `aria-current`) is covered green by `core/tests/test_rendering.py`; the full axe/WCAG2AA gate runs in CI.
- [ ] T022 [P] [US3] Measure FCP and total page weight for `/blog/sample-article/` and confirm ≤10% regression vs baseline and that no render-blocking third-party request was added (SC-007, FR-012, contract C9) — PARTIAL: confirmed no external CSS request (Pico + main.css both served from `/static/`, no third-party host, no JS added); FCP/weight numbers to be captured in a browser/Lighthouse run against the deployed build.

**Checkpoint**: Accessibility, responsiveness, no-JS, and performance all validated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gates and cleanup.

- [X] T023 Run the full quality gate: `ruff format . && ruff check . && mypy .`, then `pytest -m "not integration"` and `pytest -m integration --cov-append --cov-fail-under=80`; confirm all green and combined coverage ≥ 80% (Constitution I, II)
- [X] T024 Remove any now-dead rules left in `static/css/main.css` after the reduction and story overrides; confirm no duplicated logic vs Pico (Constitution I)
- [X] T025 [P] Update `README.md` to note the site is styled with Pico CSS (vendored static asset; light/dark via system preference)
- [X] T026 Run the full `specs/002-modern-ui-styling/quickstart.md` validation end-to-end (all manual + automated scenarios) and confirm every "Done when" item passes

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies — start immediately (T001 required before any styling shows; T002 baseline should be captured before T003 changes anything visible).
- **Foundational (Phase 2)**: depends on T001; **blocks all user stories** (edits shared `base.html` + `main.css`).
- **User Story 1 (Phase 3)**: depends on Phase 2. MVP.
- **User Story 2 (Phase 4)**: depends on Phase 2; best after US1 so overrides exist to make theme-aware, but independently testable.
- **User Story 3 (Phase 5)**: depends on Phase 2; validation is most meaningful after US1/US2, but each check is independent.
- **Polish (Phase 6)**: depends on all targeted stories being complete.

### Story independence

- US1 delivers the standalone MVP (a cohesive modern look) with no dependency on US2/US3.
- US2 and US3 harden and validate US1's output; each is independently testable per its Independent Test.

### Within a story

- Tests (T005/T006/T014) can be written before/alongside implementation.
- Tasks editing **different files** are marked `[P]`; tasks editing `static/css/main.css` (T010, T011, T012, T015, T018, T020, T024) are **sequential** to avoid conflicts.

### Parallel opportunities

- T002 runs parallel to T001-adjacent prep.
- US1 tests T005 + T006 (same file, different tests — write together) and partial edits T007 + T008 + T009 (different template files) are `[P]`.
- US3 audits T021 + T022 are `[P]` (independent measurements); T017 is `[P]` (different concern).

---

## Parallel Example: User Story 1

```text
# Different template files — safe to parallelize:
Task T007: Restyle core/templates/core/partials/nav.html
Task T008: Adjust core/templates/core/partials/footer.html
Task T009: Verify core/templates/core/blocks/*.html

# Then main.css overrides run sequentially (same file):
Task T010 → T011 → T012
```

---

## Implementation Strategy

### MVP first (User Story 1 only)

1. Phase 1: Setup (vendor Pico, capture baseline).
2. Phase 2: Foundational (wire base.html, reduce main.css). **Blocks everything.**
3. Phase 3: User Story 1 → cohesive modern look on every page.
4. **STOP and VALIDATE**: load all 7 URLs; confirm SC-001/SC-002. Demoable MVP.

### Incremental delivery

1. Setup + Foundational → Pico live.
2. US1 → cohesive style (MVP) → demo.
3. US2 → dark/light → demo.
4. US3 → accessibility/responsive/perf/no-JS validated against baseline.
5. Polish → quality gates + cleanup + quickstart validation.

---

## Notes

- `[P]` = different files, no incomplete-task dependency.
- Presentation-only feature: no models/migrations (data-model.md confirms zero entities).
- Preserve `class="skip-link"`, `.hp-field`, and `.visually-hidden` markup exactly — tests and
  accessibility/spam protection depend on them.
- Commit after each task or logical group; stop at any checkpoint to validate a story independently.
