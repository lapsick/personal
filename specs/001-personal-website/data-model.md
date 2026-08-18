# Phase 1 Data Model: Personal Professional Website

**Feature**: 001-personal-website | **Date**: 2026-08-18

This maps the spec's Key Entities onto concrete Wagtail page types, snippets, settings, and
supporting models. Field types are Wagtail/Django-conceptual; migrations and exact column types are
produced during implementation, not here.

## Page tree (site structure — FR-001, FR-004)

```text
HomePage (site root page)              /
├── AboutPage                          /about/
├── ProjectIndexPage                   /projects/
│   └── ProjectPage (0..N)             /projects/<slug>/
├── BlogIndexPage                      /blog/
│   └── ArticlePage (0..N)             /blog/<slug>/
└── ContactPage                        /contact/
```

Wagtail derives each URL from the page tree and slug, giving every page and article a stable,
shareable address (FR-004, SC-008). Navigation to all five sections is rendered from these fixed
pages (FR-002).

---

## Shared building blocks (`core` app)

### `BasePage` / `SeoMixin` (abstract)

Applied to every concrete page type. Encodes SEO + social contract (D7).

| Field | Type | Notes |
|-------|------|-------|
| `seo_title` | char (from Wagtail `Page`) | overrides `<title>` when set |
| `search_description` | text (from Wagtail `Page`) | meta description |
| `social_image` | FK → Wagtail Image (nullable) | Open Graph / Twitter card image |
| `canonical_url` | URL (nullable) | override canonical; defaults to page's full URL |

**Validation**: none required; all optional with sensible defaults derived from page fields.

### StreamField block set (rich body content — D4)

Curated, consistent component vocabulary reused by `ProjectPage` and `ArticlePage` bodies:
`heading`, `paragraph` (rich text: bold/italic/links/lists), `code` (language + text),
`image` (image + alt + optional caption), `quote`. No raw-HTML block (keeps output consistent and
safe — Principle III).

### `SiteSettings` (Wagtail settings model, editable in admin)

Owner-editable global data surfaced across pages.

| Field | Type | Notes |
|-------|------|-------|
| `owner_name` | char | used in header/footer/SEO |
| `professional_title` | char | e.g., "Software Engineer & Architect" |
| `tagline` | char | short specialization line (Home hero) |
| `resume_document` | FK → Wagtail Document (nullable) | downloadable resume (D6) |
| `contact_email` | email | fallback contact channel (FR-018, FR-020) |
| `linkedin_url`, `github_url`, `other_profiles` | URL / repeatable | professional profile links (FR-020) |
| `email_obfuscation` | derived behavior | email never rendered as raw harvestable text (FR-025) |

---

## Entity: Owner Profile → `HomePage` + `AboutPage` + `SiteSettings`

Represents the single subject of the site (spec: Owner Profile). Split across the landing page,
the about page, and global settings.

### `HomePage` (FR-005, FR-006, FR-007)

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `hero_heading` | char | yes | owner name + title, above the fold (FR-005) |
| `hero_subheading` | char | yes | specialization (.NET/Microsoft) statement |
| `primary_cta_label` | char | yes | e.g., "Get in touch" (FR-006) |
| `primary_cta_page` | FK → Page | yes | target of CTA (defaults to ContactPage) |
| `intro` | StreamField | no | short value proposition |
| `featured_projects` | M2M/orderable → ProjectPage (0..N) | no | trust signal previews (FR-007) |
| `featured_articles` | M2M/orderable → ArticlePage (0..N) | no | highlighted writing (FR-007) |

**Validation**: hero fields and CTA required so the "identity within seconds + one-click contact"
outcome (SC-001, SC-002) is structurally guaranteed.

### `AboutPage` (FR-008)

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `intro` | rich text | yes | professional summary |
| `body` | StreamField | yes | background, expertise (esp. .NET architecture) |
| `expertise_areas` | repeatable char/list | no | skill/expertise tags |
| `engagement_types` | rich text / list | no | what engagements the owner is open to |
| `resume_cta` | boolean/derived | no | surfaces `SiteSettings.resume_document` download |

---

## Entity: Work Item → `ProjectPage` (child of `ProjectIndexPage`)

Spec: Work Item. Fields per plan input (problem, role, approach, technologies, outcome).

### `ProjectIndexPage` (FR-009, FR-011)

| Field | Type | Notes |
|-------|------|-------|
| `intro` | rich text | optional lead-in |
| (lists children) | — | renders `ProjectPage` cards; **empty state** when none (FR-011) |

### `ProjectPage`

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `title` | char (Page) | yes | project name (FR-009) |
| `summary` | text | yes | short description for cards + previews |
| `problem` | rich text | yes | problem / context (spec content model) |
| `role` | rich text | yes | owner's role / contribution |
| `approach` | StreamField | yes | how it was solved |
| `technologies` | repeatable char / tags | yes | tech stack (FR-009) |
| `outcome` | rich text | yes | result / impact |
| `external_links` | repeatable {label, url} | no | live site / repo / case study (FR-010) |
| `featured_image` | FK → Image | no | card + hero image |
| `date` | date | no | for ordering |

**Validation & rules**:
- `external_links[].url` validated as URL; rendered with `target=_blank` + `rel="noopener noreferrer"`
  so external resources open without losing site context (FR-010) and broken outbound links never
  break the page (spec edge case).
- Ordering: newest/`date` desc by default on the index.

---

## Entity: Article → `ArticlePage` (child of `BlogIndexPage`)

Spec: Article. Fields per plan input (title, date, summary, body, tags).

### `BlogIndexPage` (FR-012, FR-014)

| Field | Type | Notes |
|-------|------|-------|
| `intro` | rich text | optional |
| (lists children) | — | title + date + summary per item, most-recent first (FR-012); **empty state** when none (FR-014) |

### `ArticlePage` (FR-013)

| Field | Type | Req | Notes |
|-------|------|-----|-------|
| `title` | char (Page) | yes | article title |
| `date` | date | yes | publication date (ordering, display) |
| `summary` | text | yes | list summary + meta description default |
| `body` | StreamField | yes | article content |
| `tags` | `ClusterTaggableManager` → `ArticleTag` | no | taxonomy |
| `featured_image` | FK → Image | no | header + social card |

**Validation & rules**:
- Directly linkable/shareable as its own page (FR-013, SC-008); direct entry renders full nav
  (FR-013 scenario 3).
- Index orders by `date` desc (FR-012).

### `ArticleTag` (through model for taggit)

Standard Wagtail tag through-model linking `ArticlePage` ↔ `Tag`.

---

## Entity: Contact Message → `ContactPage` + form submissions

Spec: Contact Message. `ContactPage` is a Wagtail `AbstractEmailForm` page (D5).

### `ContactPage` (FR-015..FR-019)

| Field | Type | Notes |
|-------|------|-------|
| `intro` | rich text | owner-editable lead-in + privacy notice text (D11) |
| `thank_you_text` | rich text | confirmation shown on success (FR-017) |
| `to_address` | email (Wagtail form) | owner notification target (FR-017) |
| form fields | Wagtail `FormField` rows | owner-editable; defaults below |

### Contact submission (the "Contact Message" data)

| Field | Type | Req | Validation |
|-------|------|-----|-----------|
| `name` | char | yes | non-empty (FR-015/016) |
| `email` | email | yes | valid email format (FR-016) — used as reply-to |
| `message` | text | yes | non-empty, length-bounded |
| `submitted_at` | datetime | auto | timestamp (spec entity) |
| `honeypot` | char (hidden) | must be empty | non-empty ⇒ reject as spam (D5) |
| `form_rendered_at` | signed timestamp | — | submit faster than threshold ⇒ reject (D5) |

**Behavioral rules**:
- On valid, non-spam submission: persist per retention policy (D11) and email the owner with sender
  name + reply-to + message (FR-017); show `thank_you_text` (FR-017).
- On validation failure: re-render form with field-level errors identifying the field to fix (FR-016).
- On send/delivery failure: show a clear error + fallback channels from `SiteSettings`
  (`contact_email`, profile links) (FR-018).
- Spam submissions are silently dropped without user-visible friction (FR-019).
- Data minimization + retention limit + no message-body logging (D11, privacy).

---

## Relationships summary

```text
SiteSettings ──(resume_document)──> Wagtail Document
HomePage ──(featured_projects)──> ProjectPage 0..N
HomePage ──(featured_articles)──> ArticlePage 0..N
HomePage ──(primary_cta_page)──> Page (default ContactPage)
ProjectIndexPage ──(parent of)──> ProjectPage 0..N
ProjectPage ──(external_links)──> {label,url} 0..N
BlogIndexPage ──(parent of)──> ArticlePage 0..N
ArticlePage ──(tags)──> ArticleTag ──> Tag 0..N
ContactPage ──(submissions)──> Contact Message 0..N ──(email)──> owner
All pages ──(inherit)──> BasePage/SeoMixin (social_image, canonical, search_description)
```

## Coverage check (entities & requirements → models)

| Spec entity | Realized as | Key FRs |
|-------------|-------------|---------|
| Owner Profile | HomePage + AboutPage + SiteSettings | FR-005..008, FR-020 |
| Work Item | ProjectPage (+ ProjectIndexPage) | FR-009..011 |
| Article | ArticlePage (+ BlogIndexPage, ArticleTag) | FR-012..014 |
| Contact Message | ContactPage + submission model | FR-015..019, FR-025 |
