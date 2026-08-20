# Phase 0 Research: Modern UI Restyle (Pico CSS)

**Feature**: 002-modern-ui-styling | **Date**: 2026-08-20

All Technical Context unknowns are resolved below. There were no open `NEEDS CLARIFICATION`
markers in the spec (the framework choice was made by the owner during `/speckit-specify`).

## D1. Delivery method — vendored static file vs. CDN

- **Decision**: Vendor a pinned `pico.min.css` under `static/css/vendor/` and serve it through the
  existing Django/WhiteNoise static pipeline. Do **not** load Pico from a public CDN.
- **Rationale**: A vendored asset is reproducible (no external network dependency in CI, dev, or
  prod), avoids a render-blocking third-party request (Constitution IV / SC-007), sidesteps CSP and
  privacy concerns, and is cache-busted/compressed by the existing static setup. No Node/npm build
  step is introduced, keeping the Python-only toolchain intact (Constitution: Python Environment
  Standards).
- **Alternatives considered**: (a) CDN `<link>` — rejected: external request, privacy/CSP surface,
  offline-dev breakage. (b) npm + build pipeline (e.g., importing `@picocss/pico`) — rejected:
  introduces a JS toolchain the project deliberately avoids, for no benefit at this scope.

## D2. Pico "flavor" — classless base vs. class-based (`.container`, `.grid`)

- **Decision**: Use the standard Pico build and rely primarily on its **classless** semantic
  styling (typography, forms, `<button>`, tables, `<article>`), while keeping Pico's `.container`
  wrapper (already used by templates) and a **thin project override layer** in `main.css` for the
  handful of components Pico does not provide.
- **Rationale**: Templates already emit semantic HTML, so classless Pico styles most of the page
  with near-zero markup churn (spec's core reason for choosing Pico). A small override layer keeps
  bespoke, still-needed pieces without fighting the framework.
- **Alternatives considered**: Full migration to Pico's class-based grid/components — rejected:
  more template churn than the "minimal change" goal warrants; the existing custom `card-grid`
  already works and is easy to retain.

## D3. Stylesheet load order and the role of `main.css`

- **Decision**: In `base.html`, load `vendor/pico.min.css` **before** `main.css`. Reduce `main.css`
  from a full scaffold to a thin override layer that retains only: skip link, honeypot (`.hp-field`),
  `.visually-hidden`, card grid (`.card-grid`, `.card`), nav active indicator (`.is-current`),
  tag list (`.tag-list`, `.tag`), and error emphasis (`.field-error`, `.error-summary`,
  `.form-field--error`). Remove rules now supplied by Pico (base typography, generic form control
  styling, button base, link color, container width, focus outline where Pico's is adequate).
- **Rationale**: Later-loaded project CSS can override or extend Pico deterministically. Keeping the
  override layer small reduces duplication (Constitution I) and total weight (Constitution IV).
- **Alternatives considered**: Loading `main.css` first / deleting it entirely — rejected: several
  project-specific hooks (skip link, honeypot, active nav) are not part of Pico and must persist;
  they are asserted by tests and required by accessibility/spam features.

## D4. Dark mode strategy

- **Decision**: Rely on Pico's automatic `prefers-color-scheme` theming. Set `color-scheme`
  appropriately on the document (via Pico defaults / a `<meta name="color-scheme" content="light dark">`
  or `<html>` handling) and author any override-layer colors with Pico's CSS custom properties
  (e.g., `--pico-*`) so they adapt to both themes. **No JavaScript theme toggle** in this iteration.
- **Rationale**: The spec requires following system preference by default (FR-005), not a manual
  toggle. Pico ships first-class light/dark that responds to the OS setting with zero JS, preserving
  the no-JS constraint. Authoring overrides against Pico variables guarantees both themes stay
  AA-contrast (FR-006) without maintaining two palettes by hand.
- **Alternatives considered**: JS-driven toggle with `data-theme` persistence — deferred to a
  possible follow-up; out of scope because it requires JavaScript and adds state the spec doesn't
  ask for.

## D5. Preserving accessibility & spam-protection hooks

- **Decision**: Keep `class="skip-link"`, the `.hp-field` honeypot, `.visually-hidden`, required-field
  markers, and error-summary semantics exactly as-is in markup; restyle them in the override layer so
  they remain functional and visually coherent in both themes. Keep focus-visible outlines at least as
  strong as today (use Pico's focus ring if it meets AA, else retain the custom outline).
- **Rationale**: These underpin existing accessibility and no-JS spam protection (contact form) and
  are covered by tests; they must survive the restyle untouched in behavior (FR-008, FR-009, FR-010).
- **Alternatives considered**: Dropping custom focus outline for Pico's default — accepted only if
  Pico's default meets the existing 3px AA-visible bar; otherwise retain the custom rule.

## D6. Button / CTA convention (`.button` anchors)

- **Decision**: Keep the `.button` / `.button--secondary` anchor CTAs and style them in the override
  layer to match Pico's button appearance (or add `role="button"` where an anchor should read as a
  button). Native `<button type="submit">` in the contact form is styled by Pico automatically.
- **Rationale**: Pico auto-styles `<button>` and `a[role="button"]`, but not a bare `.button` class.
  A small override (or a `role="button"` attribute) aligns the existing CTAs with Pico's look while
  keeping template churn minimal.
- **Alternatives considered**: Rewriting all CTAs to `role="button"` — acceptable but larger diff;
  the override-layer approach is lower-risk and reversible.

## D7. Pinned version & maintenance

- **Decision**: Pin a specific Pico release (record the exact version in the vendored file header and
  in `quickstart.md`) so upgrades are deliberate. Pico is actively maintained and MIT-licensed
  (license-compatible per Constitution: Python Environment Standards / dependency evaluation).
- **Rationale**: Reproducible builds and auditable upgrades; MIT license imposes no distribution
  constraints on a personal site.
- **Alternatives considered**: Tracking `latest` — rejected: silent visual/regression risk.

## Summary of decisions

| # | Topic | Decision |
|---|-------|----------|
| D1 | Delivery | Vendor pinned `pico.min.css` as static asset (no CDN, no npm) |
| D2 | Flavor | Classless Pico + retain `.container` + thin override layer |
| D3 | Load order | Pico first, reduced `main.css` second as override layer |
| D4 | Dark mode | Pico `prefers-color-scheme` auto theming; no JS toggle |
| D5 | A11y hooks | Preserve skip-link/honeypot/visually-hidden/focus; restyle only |
| D6 | Buttons | Style `.button` anchors to match Pico; native buttons auto-styled |
| D7 | Version | Pin exact Pico release; MIT license |
