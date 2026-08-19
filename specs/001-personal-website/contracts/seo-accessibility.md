# Contract: SEO, Sitemap & Accessibility

**Feature**: 001-personal-website | **Date**: 2026-08-18

Defines the acceptance contract for discoverability (FR-023, SC-008/009) and accessibility
(FR-022, SC-004). These are verifiable gates, not implementation detail.

## SEO / social metadata (every public page)

The SEO head partial MUST emit, per page:

| Tag | Source | Rule |
|-----|--------|------|
| `<title>` | `seo_title` or page title + site name | unique, descriptive per page |
| `<meta name="description">` | `search_description` or `summary` | present, ≤ ~160 chars |
| `<link rel="canonical">` | `canonical_url` or page full URL | absolute HTTPS URL |
| `og:title`, `og:description`, `og:type`, `og:url` | page fields | present on all pages |
| `og:image` | `social_image` or `featured_image` fallback | absolute URL when image set |
| `twitter:card` | `summary_large_image` when image present, else `summary` | present |

**Acceptance (SC-008)**: pasting any page or article URL into a link-preview tool shows a
descriptive title + summary (+ image when set). Verified per page type in tests.

## Sitemap & crawling (FR-023, SC-009)

- `GET /sitemap.xml` lists every **published, public** page and article with `loc` and `lastmod`;
  excludes drafts, admin, and private pages.
- `GET /robots.txt` allows crawling of public content, disallows admin paths, and references the
  sitemap.
- No `noindex` on primary content; admin/utility routes are not indexed.

**Acceptance (SC-009)**: all five page types + every published article appear in `/sitemap.xml`.

## Accessibility — WCAG 2.1 AA (FR-022, SC-004)

Structural requirements (verified by automated + manual checks):

| Area | Requirement |
|------|-------------|
| Landmarks | Semantic `header`/`nav`/`main`/`footer`; one `<h1>` per page; logical heading order |
| Skip link | Visible-on-focus "skip to content" link as first focusable element |
| Keyboard | All interactive elements (nav, links, form, submit) operable and reachable by keyboard; no traps; visible focus indicator |
| Forms | Every control has a programmatic `<label>`; errors linked via `aria-describedby` + summarized; state conveyed in text (not color alone) |
| Contrast | Text and UI meet AA contrast ratios (4.5:1 body, 3:1 large text/UI) via design tokens |
| Images | Meaningful images have alt text (enforced in Wagtail admin); decorative images have empty alt |
| Motion/JS | Core content and contact usable with JS disabled; no motion required to operate |
| Language | `<html lang>` set |

**Acceptance (SC-004)**: automated axe-core / pa11y checks on Home, About, Projects index + detail,
Blog index + article, and Contact report **zero** critical/serious violations in CI; plus a manual
keyboard-only and screen-reader pass of the four primary journeys with no blocking issue.

## Responsive (FR-021, SC-006)

- Mobile-first CSS; usable and legible from 320px to 1920px with no horizontal scroll or overflow.
- Images use responsive renditions with explicit width/height to avoid layout shift (CLS).

**Acceptance (SC-006)**: no horizontal scrolling/overflow across the 320–1920px range on all page
types.

## Performance / Core Web Vitals (SC-005, Principle IV)

- Budgets: LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms on a mid-range mobile device / typical mobile network.
- Per-page-type DB query budget documented and asserted in tests (no N+1 on index pages).

**Acceptance (SC-005)**: primary content of each page is visible/interactive within 2.5s under the
target conditions; CWV field/lab checks meet the budgets.
