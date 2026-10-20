# Google Search setup

## Local implementation

The homepage and five portfolio entry pages have descriptive search titles. Existing visible page headings are preserved. The homepage links directly to the visualization portfolio, packages, projects, statistics tutorials, and workshops. The site description identifies the author's areas of work.

`python3 scripts/render-news.py` runs after Quarto renders. It inserts the selected publisher headlines into `_site/index.html`, so they are available without JavaScript. The browser refreshes the same container from JSON. The scheduled news workflow updates both the published JSON and homepage HTML. Headlines remain attributed links; no publisher article text is copied.

## Account setup and public verification

1. Open Google Search Console and select an existing property for `https://federicagazzelloni.com/`, or add one. A Domain property requires a DNS verification record; a URL-prefix property offers alternative verification methods. Follow the verification method Google provides for the chosen property.
2. After deployment, confirm the public sitemap and robots file are accessible and that sitemap entries use the preferred custom domain.
3. Submit `https://federicagazzelloni.com/sitemap.xml` in Sitemaps.
4. Inspect the homepage and the projects, packages, visualization, workshops, and book entry pages. Use Test live URL to check rendered content and indexing eligibility. Request indexing for the key updated pages.
5. Review Page indexing and Performance reports as data becomes available. Track actual queries, impressions, clicks, and relevant landing pages before choosing further content changes.

Search Console is not connected in this session. Verification, sitemap submission, and Google indexing have not been confirmed. Local rendering is not deployment. Follow `homepage-news.md` for news automation activation.

Official guidance:
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
