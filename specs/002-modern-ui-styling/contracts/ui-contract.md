# UI Contract: Modern UI Restyle (Pico CSS)

**Feature**: 002-modern-ui-styling | **Date**: 2026-08-20

This site exposes no external API. Its "contract" is the visual/interaction contract of the
restyled public pages. Each item below is observable and testable (via rendering tests, pa11y, or
manual visual/keyboard checks) and maps to spec requirements.

## C1. Global document

- The base template MUST link the vendored Pico stylesheet (`css/vendor/pico.min.css`) **before**
  `css/main.css`. → FR-002, FR-003
- The document MUST declare support for both color schemes so the browser renders the correct native
  controls in dark and light (e.g., `color-scheme: light dark`). → FR-005
- `class="skip-link"` MUST remain the first focusable element and become visible on focus. → FR-008
  (asserted by `core/tests/test_rendering.py` and per-app flow tests)
- `<main id="main-content">`, `<header>`, and `<footer>` MUST all be present on every page. → FR-003

## C2. Navigation & footer

- The primary `<nav aria-label="Primary">` MUST render as a styled nav bar; the active item MUST
  retain a visible current-state indicator and `aria-current="page"`. → FR-003
- The footer identity, links, and copyright MUST render styled and legible in both themes. → FR-003

## C3. Content blocks (StreamField)

Each block MUST have a defined, non-broken appearance in both themes: → FR-004, SC-002

- Heading (`h2`/`h3`), Paragraph (rich text: bold/italic/link/lists), Code (`<figure>` + `<pre><code>`
  with horizontal scroll for wide code), Image (`<figure>` + optional caption, `max-width:100%`),
  Quote (`<blockquote>` + optional attribution).

## C4. Page types

- Home: hero heading/subheading, optional CTA button, intro stream, featured project/article card
  grids. → FR-001
- About, Projects index + detail, Blog index + article, Contact: consistent typography, spacing, and
  components with the rest of the site; no page falls back to unstyled/legacy appearance. → FR-001,
  SC-001, SC-008

## C5. Buttons / CTAs

- Anchor CTAs (`.button`, `.button--secondary`) and native `<button type="submit">` MUST render with
  a consistent, Pico-aligned button appearance and visible focus state. → FR-001, FR-008

## C6. Contact form (no-JS critical path)

- All form controls (inputs, textarea, labels, required markers) MUST be styled by Pico/override
  layer. → FR-009
- Error summary, per-field errors, `.form-field--error` state, and the send-failure fallback message
  MUST be clearly styled and legible in both themes. → FR-009
- The honeypot `.hp-field` MUST remain visually hidden and off-screen; the form MUST submit and
  enforce spam protection with JavaScript disabled. → FR-009, SC-006

## C7. Responsive & overflow

- No page produces horizontal scrolling at a 360px-wide viewport; images/tables/code blocks scroll
  within their own container rather than the page body. → FR-007, SC-005

## C8. Accessibility (regression gate)

- `pa11y-ci` (axe / WCAG2AA) MUST pass on all URLs in `.pa11yci.json` with zero new violations vs.
  the pre-restyle baseline. → FR-010, SC-004
- Keyboard focus MUST be visible on all interactive elements; tab order preserved. → FR-008

## C9. Performance (budget)

- No render-blocking third-party requests introduced; CSS served as cacheable static asset(s). FCP and
  total page weight MUST NOT regress > 10% vs. pre-restyle baseline on a representative page. → FR-012,
  SC-007
