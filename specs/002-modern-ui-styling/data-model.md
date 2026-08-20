# Phase 1 Data Model: Modern UI Restyle (Pico CSS)

**Feature**: 002-modern-ui-styling | **Date**: 2026-08-20

## Overview

This feature is **presentation-only**. It introduces **no new data entities, models, database
tables, migrations, or CMS field changes**. Existing content renders unchanged under the new
style (FR-011).

## Entities

None. No persistent domain data is created, modified, or removed.

## Design tokens (styling constructs — not persisted data)

For completeness, the restyle operates on the following non-persistent styling constructs, all
sourced from Pico CSS and consumed by the thin override layer. These live in CSS, not the database.

| Token group | Source | Consumed by |
|-------------|--------|-------------|
| Color roles (background, text, primary, muted, border) | Pico `--pico-*` custom properties (light + dark) | `main.css` override layer, block templates |
| Typography (font family, sizes, line height, measure) | Pico defaults | Base document, body content blocks |
| Spacing / radius | Pico defaults + a few retained project vars | Card grid, tag list, forms |
| Theme selector | `prefers-color-scheme` (auto) via Pico | Document-wide, both themes |

## State & transitions

Not applicable. The only runtime "state" is the visitor's OS color-scheme preference, which is
read by CSS at render time (no application state, no persistence, no user-set toggle in this
iteration).

## Validation rules (from requirements, expressed as presentation invariants)

- Every audited page and every StreamField block type MUST resolve to a defined, non-broken
  appearance (FR-001, FR-004).
- Text/interactive contrast MUST meet WCAG 2.1 AA in both light and dark themes (FR-006).
- No horizontal overflow at a 360px viewport (SC-005).
- Accessibility/spam-protection markup hooks (`skip-link`, honeypot, `visually-hidden`) MUST remain
  present and functional (FR-008, FR-009, D5).
