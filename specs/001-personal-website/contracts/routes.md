# Contract: URL / Page-Type Routing

**Feature**: 001-personal-website | **Date**: 2026-08-18

The site's public "interface" is its set of URLs (server-rendered HTML). Routes are derived from the
Wagtail page tree except for the platform/utility routes registered in `portfolio/urls.py`.

## Public page routes (from Wagtail page tree)

| Path | Page type | Renders | Requirements |
|------|-----------|---------|--------------|
| `GET /` | HomePage | Hero (name/title/specialization), primary contact CTA, featured projects/articles, nav | FR-002, FR-005, FR-006, FR-007; SC-001, SC-002 |
| `GET /about/` | AboutPage | Background, expertise, engagement types, resume download link | FR-008 |
| `GET /projects/` | ProjectIndexPage | List of ProjectPage cards (title, summary, tech); empty state when none | FR-009, FR-011 |
| `GET /projects/<slug>/` | ProjectPage | problem, role, approach, technologies, outcome, external links | FR-009, FR-010 |
| `GET /blog/` | BlogIndexPage | Article list (title, date, summary), most-recent first; empty state when none | FR-012, FR-014 |
| `GET /blog/<slug>/` | ArticlePage | Full article (title, date, body); directly shareable | FR-013, SC-008 |
| `GET /contact/` | ContactPage | Contact form + privacy notice + fallback channels | FR-015, FR-018, FR-020 |
| `POST /contact/` | ContactPage | Validates + processes submission (see contact-form.md) | FR-015..019 |

**Slug stability**: once published, project/article slugs SHOULD NOT change (shareable-link
guarantee, FR-004/SC-008). If a slug must change, a redirect SHOULD be added (Wagtail redirects).

## Utility / platform routes (`portfolio/urls.py`)

| Path | Purpose | Requirement |
|------|---------|-------------|
| `GET /sitemap.xml` | XML sitemap of all published pages/articles | FR-023, SC-009 |
| `GET /robots.txt` | Crawl directives; references sitemap | FR-023 |
| `GET /documents/...` | Wagtail document serving (resume download) | FR-024 (D6) |
| `GET /cms/` (or `/admin/`) | Wagtail admin — owner content editing (auth required) | FR-024 |
| `GET /django-admin/` | Django admin (auth required) | ops |

## Cross-cutting response rules (every public route)

- Consistent global navigation to all five sections is present on every page (FR-002) with a
  current-page indicator (FR-003).
- Every response includes the SEO head partial: `<title>`, meta description, canonical, and
  Open Graph / Twitter tags (FR-023). See `seo-accessibility.md`.
- All routes function with JavaScript disabled (progressive enhancement). JS is additive only.
- `404` and `500` render branded, navigable, accessible error pages (Principle III).
- All traffic served over HTTPS (platform-provided); HTTP redirects to HTTPS in production.

## Acceptance signals

- Direct entry to any deep URL (e.g. `/blog/<slug>/`, `/about/`) renders full navigation and is
  self-orienting (spec edge case "direct entry on any page").
- Index routes with zero children return HTTP 200 with a graceful empty-state, never an error
  (FR-011, FR-014).
