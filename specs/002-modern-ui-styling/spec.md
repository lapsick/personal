# Feature Specification: Modern UI Restyle (Pico CSS)

**Feature Branch**: `002-modern-ui-styling`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "Style sites with one of modern UI available in public. Propose me several for choice"

## Summary

Restyle the existing personal/professional website with a modern, publicly-available UI so
that every page presents a cohesive, contemporary visual identity instead of the current
hand-rolled minimal stylesheet. From the proposed options (Pico CSS, Tailwind CSS, Bootstrap 5,
Bulma), the owner selected **Pico CSS** — a lightweight, semantic-HTML-first framework with a
built-in light/dark theme — because it modernizes the look with minimal template churn and
preserves the site's accessibility and performance posture.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cohesive modern look across all pages (Priority: P1)

A visitor lands on the site (Home, About, Projects, Blog, Contact) and experiences a single,
polished, contemporary visual style: consistent typography, spacing, colors, buttons, links,
cards, and form controls on every page and content block.

**Why this priority**: The core purpose of the feature is a modern, consistent look. Without
this, nothing else matters. This slice alone delivers the primary value.

**Independent Test**: Navigate to each top-level page and visually confirm shared typography,
spacing, and component styling; confirm no page falls back to unstyled or legacy appearance.

**Acceptance Scenarios**:

1. **Given** the restyle is applied, **When** a visitor opens any of Home, About, Projects,
   Blog, or Contact, **Then** the page renders with the new UI system's typography, spacing,
   colors, and component styles consistently.
2. **Given** a Wagtail StreamField page with headings, paragraphs, lists, images, quotes, and
   buttons, **When** it is viewed, **Then** every block is styled by the new UI system with no
   unstyled or visually broken elements.
3. **Given** the navigation bar and footer, **When** any page loads, **Then** they adopt the new
   UI styling and remain visually consistent across pages.

---

### User Story 2 - Light and dark appearance (Priority: P2)

A visitor viewing the site in a dark-mode environment (or toggling appearance) sees a
first-class dark theme with legible contrast, and a light-mode visitor sees the light theme —
both drawn from the same modern UI system.

**Why this priority**: Modern sites are expected to respect appearance preferences; the chosen
system provides this out of the box, so it is high-value but secondary to the base restyle.

**Independent Test**: Set the OS/browser to dark mode and load each page; confirm a coherent
dark theme with readable text; switch to light mode and confirm the light theme.

**Acceptance Scenarios**:

1. **Given** the visitor's system prefers dark mode, **When** any page loads, **Then** the site
   renders a dark theme with text and interactive elements meeting contrast requirements.
2. **Given** the visitor's system prefers light mode, **When** any page loads, **Then** the site
   renders the light theme with text and interactive elements meeting contrast requirements.

---

### User Story 3 - Accessible, responsive, and fast after restyle (Priority: P2)

A visitor on a phone, tablet, or desktop — including keyboard and screen-reader users —
continues to navigate, read, and submit the contact form successfully after the restyle, with
no regression in accessibility or load performance.

**Why this priority**: The restyle must not degrade the site's existing accessibility,
responsiveness, or performance guarantees; a modern look that breaks these is a net loss.

**Independent Test**: Run the accessibility check on key pages, verify keyboard focus visibility
and tab order, resize across breakpoints, and confirm the contact form still submits without
JavaScript.

**Acceptance Scenarios**:

1. **Given** the restyled site, **When** the automated accessibility check runs on Home, About,
   Projects, Blog, and Contact, **Then** it passes with no new violations.
2. **Given** a keyboard-only visitor, **When** they tab through navigation, links, and form
   fields, **Then** focus is always visible and the tab order is logical.
3. **Given** a visitor on a narrow (mobile) viewport, **When** they view any page, **Then**
   content reflows without horizontal scrolling and remains readable.
4. **Given** the contact form, **When** it is submitted with JavaScript disabled, **Then** it
   still works (including existing spam protection) and displays styled success/error states.

---

### Edge Cases

- **Long-form content**: Very long articles, long project descriptions, wide code blocks, and
  wide tables must remain readable and must not overflow the viewport horizontally.
- **Legacy/custom styles**: Any element that previously depended on the hand-rolled stylesheet
  (skip link, honeypot field, focus outlines) must remain functional and correctly hidden/shown.
- **Missing content**: Pages with empty optional fields (no hero image, no tags, empty index)
  must still render cleanly with no broken layout.
- **Rich embedded media**: Wagtail-embedded images and any embeds must scale within their
  container and not break the grid.
- **Form validation states**: Field errors, required-field markers, and the send-failure
  fallback message must be clearly styled and legible in both light and dark themes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST present a single, consistent modern visual style across all
  top-level pages (Home, About, Projects, Projects detail, Blog, Blog article, Contact).
- **FR-002**: The restyle MUST use a publicly-available, actively-maintained UI framework
  (selected: Pico CSS) rather than bespoke per-page styling.
- **FR-003**: All shared layout elements (navigation, footer, skip link, main content region)
  MUST adopt the new styling and remain consistent on every page.
- **FR-004**: Every curated content block available in the page editor (headings, paragraphs,
  rich text, lists, images, quotes, buttons/CTAs, and any other existing block types) MUST have
  a defined, non-broken appearance under the new style.
- **FR-005**: The site MUST provide both a light and a dark appearance, following the visitor's
  system preference by default.
- **FR-006**: Text and interactive elements MUST meet WCAG 2.1 AA contrast in both light and
  dark themes.
- **FR-007**: The restyle MUST preserve responsive behavior: content reflows cleanly from mobile
  through desktop with no horizontal overflow.
- **FR-008**: Keyboard focus indicators MUST remain clearly visible and the logical tab order
  MUST be preserved after the restyle.
- **FR-009**: The contact form MUST retain full no-JavaScript functionality (submission, spam
  protection, success and error states) with the new styling applied to all form controls and
  messages.
- **FR-010**: The restyle MUST NOT introduce any new automated accessibility violations on the
  audited pages.
- **FR-011**: The restyle MUST NOT require the site owner to change how they author content in
  the CMS; existing pages MUST render correctly under the new style without content re-entry.
- **FR-012**: The restyle MUST preserve or improve page load performance; it MUST NOT introduce
  render-blocking assets or heavyweight client-side dependencies that measurably slow first
  paint.

### Key Entities

Not applicable — this feature changes presentation only and introduces no new data entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of top-level pages (Home, About, Projects index + detail, Blog index +
  article, Contact) render with the new consistent visual style, verified by visual review.
- **SC-002**: Every content block type available in the editor has a defined styled appearance,
  with zero blocks rendering unstyled or visually broken.
- **SC-003**: Both light and dark themes are available and applied automatically per system
  preference on 100% of pages.
- **SC-004**: The automated accessibility check passes on all audited pages with zero new
  violations compared to the pre-restyle baseline.
- **SC-005**: No page produces horizontal scrolling at a 360px-wide mobile viewport.
- **SC-006**: The contact form submits successfully with JavaScript disabled after the restyle,
  including spam protection, in 100% of test attempts.
- **SC-007**: First-contentful-paint and total page weight do not regress by more than 10%
  against the pre-restyle baseline on a representative page.
- **SC-008**: A first-time visitor rates the site as visually "modern and cohesive" (qualitative
  review against the chosen system's reference look), with no page appearing to use a different
  style.

## Assumptions

- **Selected system**: The owner selected **Pico CSS** from the proposed options (Pico CSS,
  Tailwind CSS, Bootstrap 5, Bulma). Pico is a classless/semantic-first, lightweight framework
  with built-in light/dark theming, chosen to minimize template churn and preserve accessibility
  and performance.
- **No build pipeline required**: Pico can be served as a static stylesheet, so introducing a
  Node/JavaScript build step is out of scope; the framework's stylesheet is vendored/served
  through the existing static-asset setup.
- **Presentation-only change**: No data models, page types, CMS field definitions, or URL
  structure change. Existing content renders as-is under the new style.
- **Existing semantic HTML**: Current templates already use semantic, accessible markup, which
  Pico styles directly; only minimal wrapper/class adjustments are expected where needed.
- **Accessibility gate retained**: The existing automated accessibility check remains the
  acceptance gate for the restyle; the pre-restyle result is the baseline.
- **Scope boundary**: This feature covers the public-facing site only. The Wagtail admin
  interface is out of scope and keeps its own styling.
- **Theme customization**: Light adoption of the framework's default palette/typography is
  assumed; extensive bespoke brand theming beyond the framework's tokens is out of scope for
  this iteration and can be a follow-up.

## Dependencies

- Depends on the existing server-rendered template layer (base template, navigation/footer
  partials, StreamField block templates) as the integration surface for the new styles.
- Depends on the existing accessibility check tooling to validate no regressions.
- Requires the Pico CSS stylesheet to be available as a served static asset.
