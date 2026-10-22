# Homepage news

The homepage includes headline links in its generated HTML through `scripts/render-news.py`; JavaScript refreshes them from `data/news.json` when available. Its dedicated `scripts/news.css` avoids relying on cached copies of the site-wide stylesheet. Publisher feeds are fetched only by `scripts/update-news.py` (Python 3 standard library). The selection contains titles, links, publishers and dates, without summaries or article text. `data/news-feeds.json` controls sources and the 45-day freshness window. R and Python each receive a place when both have eligible entries. Each refresh replaces the selection, caps topics at two, and deduplicates links and titles globally.

## Local maintenance

```sh
python3 -m unittest discover -s scripts/tests -v
python3 scripts/update-news.py
quarto render index.qmd
```

Failures retain only that source's previously selected, still-recent items. A successful empty feed clears its prior selection. `checked_at` records each attempt; `last_updated_at` records the latest run with at least one successful feed. Individual `last_success_at` values reveal partial failures. The browser also hides expired/future headlines and labels delayed updates after 12 hours. Malformed feeds are treated as unavailable. GitHub logs include failures.

## Verified feeds (20 October 2026)

- OpenAI: `https://openai.com/news/rss.xml` — latest observed 19 October 2026.
- Actuarial Association of Europe: `https://actuary.eu/feed/` — latest observed 15 October 2026.
- R Project: `https://blog.r-project.org/index.xml` — latest observed 22 September 2026.
- Python Software Foundation: `https://blog.python.org/feeds/posts/default?alt=rss` — latest observed 13 October 2026.
- ECDC: `https://www.ecdc.europa.eu/en/taxonomy/term/2942/feed` — latest observed 16 October 2026; headlines identify week 42 / October 2026 reports, consistent with feed dates.

Excluded: WHO's tested news feed assigned a 10 October 2026 date to a release identified by its URL as 27 August 2020, so it was excluded despite being accessible. IHME's tested `/rss.xml` returned 404. IAA's accessible feed last showed March 2026; Posit's tested blog feed returned 404; tidyverse's tested feed was malformed XML. Dates refer to the feeds as observed, not independently verified article contents.

## Activation after review

Live GitHub Pages settings were inspected: branch deployment (`legacy`), `gh-pages`, root `/`. The existing podcast workflow only changes source posts. `_publish.yml` also contains a Netlify destination; this updater targets the verified GitHub Pages deployment only.

1. Review and commit the implementation on the repository's default branch, then publish the Quarto site through the usual process so the homepage, JavaScript and initial JSON reach `gh-pages`. The implementation was approved and pushed to `main` on 20 October 2026; the homepage and news assets were also pushed to `gh-pages`.
2. Add an expiring, repository-scoped fine-grained token as Actions secret `NEWS_DEPLOY_TOKEN`, with Contents read/write and Pages read/write permissions. It must be authorised for this repository and allowed by branch rules. No token belongs in a source file. The normal `GITHUB_TOKEN` cannot reliably trigger a new Pages build from a branch push, hence this explicit credential.
3. Enable Actions and run **Refresh homepage news** manually. The workflow checks out the current `gh-pages`, uses its JSON as the cache, updates `data/news.json` and embeds the same selection in the published `index.html`, pushes without force, and explicitly requests a Pages build. It preserves the rest of the published site. A missing news container stops publication so that an older homepage cannot silently receive a partial update.
4. Confirm the Pages build succeeds and inspect the public `data/news.json` and homepage timestamp. Subsequent runs are scheduled at minute 17 every six hours (UTC). GitHub schedules can be delayed and can be disabled on inactive public repositories; monitor failed runs and token expiry.

Publication was approved on 20 October 2026. No repository settings or secrets were changed; `NEWS_DEPLOY_TOKEN` was absent at the activation check. Until activation and a successful public check, automatic updates are not confirmed active. A later normal site publication can overwrite the JSON with the local copy: run the updater before publishing, or let the next scheduled refresh replace it. If deployment moves to Netlify, adapt the deployment step before relying on this workflow.


## Token repair verified — 22 October 2026

The existing **Homepage news updater** fine-grained token had no selected repository and no repository permissions. With user approval, its access was restricted to `fgazzelloni/fgazzelloni.github.io`, with Contents and Pages read/write plus required Metadata read. The existing expiry remains 18 January 2027. No credential value was displayed, regenerated, or copied.

Run https://github.com/fgazzelloni/fgazzelloni.github.io/actions/runs/39815727660 passed and pushed `08c684f`. A full-site publication (`b12bc8b`) one minute later replaced the refreshed JSON with the older local copy. A second approved refresh, https://github.com/fgazzelloni/fgazzelloni.github.io/actions/runs/39817484330, succeeded, followed by successful Pages deployment https://github.com/fgazzelloni/fgazzelloni.github.io/actions/runs/39817525920.

Public verification: `data/news.json` reports `last_updated_at` = `2026-10-22T16:51:04.803623+00:00` (18:51 Rome time), and all eight headlines are present in the served homepage HTML. Automatic publication now has a verified successful path; future scheduled runs and token expiry still require normal operational attention. Refresh the local news JSON before full-site publication, or rerun the news workflow afterward, to avoid overwriting fresh news with an older local snapshot.
