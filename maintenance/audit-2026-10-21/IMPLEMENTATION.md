# Website restructuring — implementation and validation

Date: 21 October 2026. Status: implemented locally; not published.

## Completed plan

1. Preserve the baseline and existing user changes. Existing generated output was copied to `/tmp/website-before-restructure-20261021/_site` before rendering. The prior footer About link remains present. All 55 original HTML page paths remain.
2. Implement the agreed navigation and destinations.
3. Apply related content, image, accessibility, and responsive fixes.
4. Render, inspect representative desktop/mobile views, test menus and links, and correct issues.
5. Save validation evidence and a reviewable local preview. Publication and hosting migration remain separate.

## Implementation changes

- `_website.yml`: Tools & Teaching; Books; Notes & Research; Consultancy; About; external DataMetricus link. Newsletter uses a Substack orange accent with darker text. Existing workshop sections remain reachable through Workshops & Materials. Podcasts are linked from HMSID. Analytical projects remain linked from Notes, the homepage, and Consultancy.
- `index.qmd`: broader professional introduction, Books and Apps actions, HMSID feature, MASTA and CP2 cards, routes to teaching/tools/consultancy, Notes wording, newsletter accent, and external news below the author's learning resources. The rotating welcome banner was restored at the user’s request. A local `scripts/running-text.js` animation retains the original messages, supports reduced motion, restarts on browser history restores, and never renders an empty string. The CDN dependency was removed. Browser navigation Home → About → Back and 1,500 simulated animation frames passed.
- `content/books/index.qmd`: three-book overview with distinct access/status labels.
- New `content/books/posts/masta/index.qmd`: title, both authors, purpose, and in-progress status. No private working materials copied.
- New `content/books/posts/cp2/index.qmd`: forthcoming release, ACTEX sign-up/purchase conditions, and user-supplied Actuarial University destination. It does not imply CP2 is already released.
- `content/books/posts/hmsid/index.qmd`: consolidated podcasts, resources, the user-supplied introductory video, and the DSLC book-club playlist. Both YouTube destinations were inspected in the browser and their titles confirmed.
- New `consultancy.qmd`: DataMetricus services, a brief explanation of AI/workflow automation, a clearly illustrative monitoring workflow, and consultancy/contact links. No client claims were added.
- `content/blog/index.qmd`: renamed visible Blog labels to Notes, distinguished individual notes from the newsletter, and retained original URLs.
- New `content/apps/index.qmd`: screenshots and descriptions for Oregon Frogs, Pathogens 2019, and Word Prediction; separate launch tabs; historical COVID dashboard link and archived-project labels. Initial app screens loaded and were captured. This is not an end-to-end app functionality test, and no hosting/settings were changed.
- `about/profile/_profile-body.qmd`: changed HMSID wording from forthcoming to published and removed undated upcoming-workshop wording.
- Content image metadata and figure alternatives: supplied explicit feature image metadata and `fig-alt` attributes. These are descriptions of images/figures, not independently validated conclusions about the underlying data.
- Replaced a failed shortened IHME reference with the direct GBD 2019 Ebola factsheet. Removed the unsupported numerical rate attached to that failed link rather than carrying it forward as verified.
- `styles.css`: responsive cards, status labels, newsletter accent, compact desktop navbar spacing, visible keyboard focus, full site name at narrow widths, and wrapping mobile footer links.
- `scripts/normalize-sitemap.R`: deduplicates URLs after normalisation, preventing duplicates introduced by incremental renders.

## Asset changes

Original images were retained. Five podcast covers now reference WebP derivatives: approximately 43.4 MB combined became 0.58 MB (about 99% smaller). The risk-assessment feature already had a WebP derivative, now refreshed, and the profile image now has a roughly 111 KB WebP derivative instead of loading the 1.7 MB PNG. See `image-optimisation.json` for exact byte counts. Actual app screenshots are saved in `images/apps/` with WebP display derivatives.

## Checks completed

- Full Quarto website render passed: 59 pages. Subsequent affected-page renders passed after the final content/layout edits. The final stylesheet was copied to `_site/styles.css` and verified byte-for-byte against source.
- Static scan: no missing local linked files/assets, no unresolved local HTML anchors, one H1 per page, and zero image elements missing an `alt` attribute across 59 pages. This is a structural check, not a complete accessibility certification.
- Every original HTML page path remains available; four pages were added.
- New navbar labels and existing footer About route appear throughout rendered HTML.
- Sitemap deduplication passed: 59 entries, with one location per page.
- Homepage responsive checks used same-origin iframe viewports at 320, 375, 390, 430, 768, 1024, and 1440 px. No horizontal overflow after fixes. Desktop navbar inspected at 1280 px and compact desktop at 1024 px. These are browser viewport checks, not physical-device testing.
- Books inspected at desktop and 390 px; Apps at desktop and 390 px; MASTA, CP2, and Consultancy at 320 px. Representative images and card layouts inspected visually.
- Mobile hamburger and Books dropdown opened successfully. Notes & Research dropdown opened by keyboard Enter and closed by Escape. Newsletter styling inspected.
- Seven existing news updater/rendering tests passed. No new test files were added.
- Source `git diff --check` passed for QMD, CSS, YAML, and the sitemap R script.

## Evidence and files

- `restructured-validation.json`: final static checks.
- `responsive-validation.json`: observed viewport measurements. The `menuButton` field records element presence, not whether the button is visible at desktop widths.
- `previews/`: desktop Books, homepage book cards, app gallery, mobile homepage, and newsletter-menu screenshots.
- `changed-files.txt`: changed/new file inventory, including generated output and pre-existing changes. It is not an attribution of every listed change to this session.

## Remaining review boundaries

- Not published, committed, or pushed. Live site still shows the prior structure.
- No Shiny app migration, repair, archived-app restoration, or full prediction/map workflow test.
- No fresh Lighthouse score, Google Analytics collection check, Search Console/indexing verification, full keyboard audit, or full contrast audit. The image payload reductions are measured file sizes, not a measured performance score.
- Historical external-link responses that were blocked/inconsistent remain unresolved; they were not treated as broken solely because automated access failed.
- Existing welcome-video captions/transcript and final HMSID bibliographic-year verification remain editorial review items. The existing publication-year labels were retained.
