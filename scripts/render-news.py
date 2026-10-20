#!/usr/bin/env python3
"""Embed the current headline selection in a rendered homepage, without network access."""
import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


def render(data, now):
    cards = []
    cutoff = now - timedelta(days=data['freshness_days'])
    for topic in data['topics']:
        rows = []
        for item in data['items']:
            stamp = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
            url = urlsplit(item['url'])
            if item['topic'] != topic['id'] or not cutoff <= stamp <= now:
                continue
            if url.scheme not in ('https', 'http') or not url.netloc:
                continue
            rows.append(f'<li><a href="{escape(item["url"], quote=True)}">{escape(item["title"])}</a>'
                        f'<p class="news-meta">{escape(item["publisher"])} · '
                        f'<time datetime="{escape(item["published_at"], quote=True)}">{stamp:%d %b %Y}</time></p></li>')
            if len(rows) == 2:
                break
        content = '<ul>' + ''.join(rows) + '</ul>' if rows else '<p class="news-meta">No recent headlines available.</p>'
        cards.append(f'<section class="news-topic"><h3>{escape(topic["title"])}</h3>{content}</section>')
    return ''.join(cards)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', type=Path, default=Path('_site'))
    args = parser.parse_args()
    page = args.site / 'index.html'
    data = json.loads((args.site / 'data/news.json').read_text())
    source = page.read_text()
    pattern = r'(<div id="news-topics" class="news-grid">).*?(</div>)'
    result, count = re.subn(pattern, lambda match: match[1] + render(data, datetime.now(timezone.utc)) + match[2], source, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one homepage news container')
    result = re.sub(r'(<p id="news-status"[^>]*>).*?(</p>)',
                    lambda match: match[1] + 'Headlines from publisher feeds; article dates are shown above. Live updates require JavaScript.' + match[2],
                    result, flags=re.S)
    page.write_text(result)


if __name__ == '__main__':
    main()
