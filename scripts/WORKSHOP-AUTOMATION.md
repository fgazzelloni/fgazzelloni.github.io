# Updating workshops and talks

## What the pilot does

`sync-workshops.py` imports completed R-Ladies Rome workshops, talks, and
tutorials where Federica is explicitly marked as a presenter or co-instructor.
Writing a recap or hosting a guest speaker does not qualify a session.

The importer reads public recap sources from the R-Ladies Rome repository's
`main` branch at a single commit. It never rewrites the recap or publishes a
website. Existing cards, abstracts, links, and filters are preserved.
Remote imports also check that the public recap is available with its expected
title. A failed or incomplete source-site deployment therefore stops the import.

The imported register is `data/teaching-events.json`. Cards are generated
between markers in `about/rladies/_rladies-body.qmd`, which is shared by the
R-Ladies page and Workshops & Talks. Do not edit those generated cards by hand;
change the source recap instead. A recap URL is the event's stable identifier.
Later edits to a recording or materials update the same entry.

This first source covers R-Ladies Rome. Conference, Carpentries, and DSLC
sections remain as they are. Importing those sources is a separate extension;
do not place unrelated events in the R-Ladies register.

## Adding a new recap

In the R-Ladies Rome repository, keep the usual `title`, `date`, `description`,
and video shortcode. Add this block to the YAML header, before the closing
`---`:

```yaml
teaching:
  presenters:
    - id: fgazzelloni
      role: presenter
  kind: workshop
  topic: "AI & machine learning"
  summary: "A short description of what participants learn."
  materials:
    - label: "Workshop guide and code"
      url: "https://github.com/fgazzelloni/your-workshop"
```

Use `co-instructor` when appropriate. Session `kind` can be `workshop`, `talk`,
or `tutorial`. The date is the session date, not the recap publication date.
Future sessions are ignored until that date. Topics must match the existing
workshop filter options; the importer reports an error for an unknown topic.

Keep the recording in the normal recap body:

```text
{{< video https://youtu.be/Zi4eCdxLLIo >}}
```

A materials-only session is allowed; add the video later to update its card.
If the recap embeds multiple videos, specify `teaching.recording_url` to
choose the session recording explicitly. Preserve the recap path once used.

## Running locally

Use a dedicated Python environment from the personal-site root:

```bash
python3 -m venv /tmp/workshop-sync-env
/tmp/workshop-sync-env/bin/python -m pip install -r scripts/requirements-workshops.txt
/tmp/workshop-sync-env/bin/python scripts/sync-workshops.py
```

To preview unpublished metadata from a local R-Ladies checkout instead:

```bash
/tmp/workshop-sync-env/bin/python scripts/sync-workshops.py --source-dir /path/to/website-italy-rladiesrome
```

Then test and render the two affected pages:

```bash
/tmp/workshop-sync-env/bin/python -m unittest discover -s scripts/workshop-tests -p 'test_sync_workshops.py' -v
quarto render about/rladies/index.qmd --profile workshop-preview
quarto render about/workshops/index.qmd --profile workshop-preview
python3 scripts/check-workshop-pages.py
```

The preview profile skips unrelated whole-site post-render tasks. It does not
change the production configuration. Check the rendered pages at desktop and
phone widths before publishing.

## Daily review workflow

Once `.github/workflows/sync-workshops.yml` is on the personal repository's
default branch, it checks daily at 07:43 UTC (08:43 Rome in winter, 09:43 in
summer). It can also be run manually under Actions → Prepare workshop updates.

When content changes, it runs tests, renders both affected pages, checks their
links against the register, and uploads a `workshop-preview` artifact. It pushes
only the register and card include to `codex/refresh-teaching-events`, then
opens or updates one draft pull request. An unchanged run does not create a
new PR. An unavailable or malformed source fails the run before content is
written; previously imported events are retained if removed from the source.

The workflow uses the repository's temporary `GITHUB_TOKEN`; no new personal
token is required. GitHub repository settings must allow Actions to create
pull requests. If that permission is disabled, the run reports the failure;
enable it under Settings → Actions → General → Workflow permissions if you
want this workflow to open PRs. No setting is changed by the importer.

Review and merge the draft when ready, then use the site's normal publication
process. This workflow never merges a PR or publishes the website.
