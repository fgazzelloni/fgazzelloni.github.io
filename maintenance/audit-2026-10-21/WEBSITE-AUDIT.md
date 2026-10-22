# Website baseline audit — 21 October 2026

## Scope and preservation

Read-only review of the website sources, 55 existing rendered HTML pages, public homepage desktop screenshot/accessibility tree, internal paths and fragments, metadata, asset sizes, and public link responses. The seven existing news tests passed. Existing changes across 54 generated HTML files and sitemap were preserved. No site source, published content, configuration, or app settings changed. No full render was run because this review examines the existing baseline without replacing generated files.

## Findings and recommended order

### 1. Update dated and inconsistent content

- `about/profile/_profile-body.qmd:10` still describes HMSID as "to be published", conflicting with published-book presentation elsewhere. The same body is shared by About and profile pages.
- The profile also refers to an undated "upcoming workshop". Replace with dated, verified information or remove the relative-time wording.
- Verify the book publication year against the publisher before carrying the current 2025 label into redesigned cards; this audit does not establish the correct bibliographic year.
- Books currently lists HMSID only. Introduce CP2 with ACTEX access conditions and MASTA as in progress, using approved descriptions.
- Separate historical technical examples and COVID apps from maintained resources. Age alone does not invalidate an article.

### 2. Improve image accessibility and delivery

- The static scan found 93 image elements without an `alt` attribute across the rendered site. This is an element count, not 93 unique images or a full WCAG assessment. Some listing thumbnails duplicate adjacent titles; decide whether each needs informative text or an explicit empty alt. Give analytical charts meaningful descriptions.
- Five podcast PNG covers are approximately 8.6–8.9 MB each (43.4 MB combined). The risk-assessment article image is 5.9 MB; profile image is 1.7 MB. Export appropriately sized WebP/AVIF derivatives and verify their rendered appearance.
- The homepage already uses an approximately 80 KB WebP hero and lazy loading for the book cover. Preserve these optimisations.
- Homepage video markup has no caption track or adjacent transcript. Review its audio and provide captions/transcript where needed; audio was not assessed.

### 3. Improve navigation and homepage balance

Agreed proposed navbar: Tools & Teaching; Books; Notes & Research; Consultancy; About; external DataMetricus link on the right. Provide a dedicated consultancy page explaining AI/workflow automation. Rename Blog display labels to Notes while preserving URLs. Use an accessible Substack orange accent for Newsletter.

The desktop homepage currently has a substantial navbar, publication announcement, animated banner, and large hero heading before the first actions. It strongly repeats AI messaging in the banner, heading, primary action, and pathway. Consider simplifying the animated banner and using the hero to describe the full professional scope. These are design proposals, not demonstrated defects.

Feature HMSID and MASTA together; include CP2 in Books with clear paid ACTEX access. Build the Shiny gallery with screenshots, dates, status, and separate launch links. Historical/archived apps should be labelled. Place own books, teaching, tools, and writing ahead of external news if professional discovery is the priority.

### 4. Review external references

207 unique external URLs were probed with a public HTTP request. 193 returned a successful response; 14 require interpretation or follow-up. Success establishes reachability only, not correctness or source quality.

- `https://bit.ly/40dboLg` returned 404, linked from the performance-metrics article at line 134. Replace with a verified direct source supporting the actual claim.
- The Washington multiple-testing lecture returned 404 to the network probe, but the web retrieval tool could retrieve PDF content. Treat as inconsistent, not conclusively dead.
- The old HTTP caret documentation and JStatSoft reference refused connection during this check. Verify manually before replacement.
- Nine URLs returned 403/406 responses, including publishers and news providers. These may block automated checks; do not remove them solely on this evidence.
- One Quarto Pub URL contains a Unicode dash and was not correctly encoded by the probe; it remains unverified, not classified as broken.

See external-links.json for raw responses. Query fragments and redirects were not systematically audited.

## Checks that passed

- 55 rendered HTML pages and 55 sitemap locations inventoried.
- Each scanned page has one H1, a nonempty description, and a canonical link. This checks presence, not title uniqueness, optimal wording, or search performance.
- No missing relative/root-local linked files or assets found by the parser, and no unresolved local HTML anchor targets.
- Eleven unique separately deployed book/package/portfolio/workshop URLs returned HTTP 200, including legacy GitHub-domain redirects.
- Public homepage inspected in the browser at desktop width; no obvious desktop overlap in the inspected viewport.
- Public robots.txt, sitemap.xml, and DataMetricus homepage returned HTTP 200. This does not confirm robots policy, sitemap submission, Google indexing, or rankings.
- Seven news updater/rendering unit tests passed.
- Reduced-motion handling and visible keyboard-focus CSS exist in reviewed source. This does not establish complete keyboard accessibility.

## Checks still needed before redesign sign-off

- Fresh mobile browser checks at 320, 375, 390, 430, and 768 px, including navigation expansion, dropdowns, horizontal overflow, and content pages. Current browser control did not provide a usable viewport-resize facility; mobile CSS inspection and historical results are not current visual proof.
- Fresh Lighthouse/PageSpeed measurements for representative pages. Asset sizes are measured; current performance scores and Core Web Vitals are not.
- Full keyboard and contrast checks, search interaction, video captions/audio, and representative workshop filters.
- Analytics consent/collection and Search Console verification, if those account-level checks are wanted. No fresh analytics or indexing assertion is made.
- A clean render and local-versus-live comparison after changes, preserving current unpublished output. This audit does not certify that local and deployed pages are identical.

## Implementation sequence

1. Correct dated wording and verified failed references; add appropriate image alternatives and optimise large images.
2. Implement the agreed navigation and dedicated book/consultancy/app pages, preserving existing URLs.
3. Rebalance homepage content and apply the newsletter accent.
4. Render and inspect desktop/mobile pages, retest links and accessibility, and obtain fresh performance measurements before publication.
