# Website findings — 22 October 2026

## Changes

- `about/profile/_profile-body.qmd`: shortened the shared About/profile copy and connected it to current research, teaching, community, writing, and consultancy work.
- `content/rpackages/index.qmd`: corrected typeR to describe simulated script typing.
- `index.qmd`: renamed Recent work to Selected guides and removed the claim that the cards show the latest writing.
- `content/books/posts/hmsid/index.qmd`: distinguished the legacy online date from the 2025 print edition.
- Separate hmsidR project: updated `index.qmd`, `CITATION`, and `_book.yml`. Replaced Pre-order, corrected the print citation year and ISBN, updated the citation URL, and removed the agreement date from publication metadata. The original date remains explained in the preface. `book-publication.patch` records these changes.

## Checks

- Full website: 59 pages rendered to `/private/tmp/site-finding-review`; expected temporary-output directory warning only. A warning during the earlier partial homepage render about missing feed targets was resolved by the full render.
- Book preface rendered to `/private/tmp/book-finding-review` using installed R libraries with `RENV_CONFIG_AUTOLOADER_ENABLED=false`; the project's existing renv cache has broken symlinks. Dependencies were not changed.
- Generated HTML assertions passed for all changed content, both citation formats, ISBN, and absence of Pre-order in the book preface.
- About inspected in the local browser at a narrow viewport; text and layout readable.
- Existing unrelated working-tree changes preserved. No commit, push, or publication performed.

## News verification

Live served JSON: `https://federicagazzelloni.com/data/news.json`.
Both `checked_at` and `last_updated_at`: `2026-10-20T16:51:55.931058+00:00` (18:51 Rome time).

Latest inspected scheduled run: https://github.com/fgazzelloni/fgazzelloni.github.io/actions/runs/39774112703
Started 22 October 2026 at 11:54 UTC. All seven tests passed; selected eight headlines with five feeds available. Publication failed with:

> Permission to fgazzelloni/fgazzelloni.github.io.git denied to fgazzelloni.
> The requested URL returned error: 403

The schedule is active, but automatic publication is not working. The credential in `NEWS_DEPLOY_TOKEN` needs repository write authorization checked (including repository selection, Contents write permission, and any required organisation approval). After correcting access, rerun the workflow and verify successful deployment plus changed served JSON and homepage. No credential or repository permission was changed in this review.
