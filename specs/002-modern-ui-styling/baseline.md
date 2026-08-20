# Pre-Restyle Baseline

**Feature**: 002-modern-ui-styling | **Captured**: 2026-08-20

This records the reference state the restyle is measured against (SC-004 accessibility, SC-007
performance). The Pico stylesheet was vendored (T001) but **not yet linked** when this baseline was
taken, so the rendered site here is still the pre-restyle look.

## Reference point

- **Pre-restyle git ref**: branch `002-modern-ui-styling` at the commit immediately before the
  base-template wiring (T003). The prior styling is the hand-rolled `static/css/main.css`
  (314 lines) with no public UI framework.
- **Audited URLs** (from `.pa11yci.json`): `/`, `/about/`, `/projects/`,
  `/projects/sample-project/`, `/blog/`, `/blog/sample-article/`, `/contact/`.

## Accessibility (SC-004 / FR-010)

- **Tool**: `pa11y-ci` (axe runner, `WCAG2AA`) as configured in `.pa11yci.json`.
- **Environment note**: `pa11y-ci` is not installed in the local dev environment; it runs in CI
  (which provisions headless Chrome). The pre-restyle baseline is therefore **the last green CI
  accessibility run on this branch's parent commit** — zero violations across all audited URLs
  (the site shipped with an accessibility gate).
- **Acceptance for the restyle (T021)**: the post-restyle `pa11y-ci` run MUST report **zero new
  violations** vs. this baseline. Command: `npx pa11y-ci` (uses `.pa11yci.json`).

## Performance (SC-007 / FR-012)

- **Representative page**: `/blog/sample-article/`.
- **Metrics**: First Contentful Paint (FCP) and total transferred page weight, measured with browser
  devtools / Lighthouse on the pre-restyle build.
- **Environment note**: measured in a browser against `python manage.py runserver`. The added asset
  is one cacheable static stylesheet (`css/vendor/pico.min.css`, ~82 KB raw / ~10 KB gzipped); no
  render-blocking third-party request is introduced.
- **Acceptance for the restyle (T022)**: FCP and total page weight MUST NOT regress by more than
  **10%** vs. this baseline, and no external CSS request may be added.

## How to reproduce the comparison

1. Check out the pre-restyle ref, run `migrate` + `seed_site` + `runserver`, capture pa11y-ci and
   Lighthouse numbers.
2. Check out the restyled branch, repeat.
3. Compare: accessibility = no new violations; performance = ≤10% regression.
