#!/usr/bin/env python3
"""Fetch headline metadata only; Python standard library, no browser RSS requests."""
import argparse
import email.utils
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[1]


def date(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        result = email.utils.parsedate_to_datetime(value)
    if result.tzinfo is None:
        raise ValueError('Date has no timezone')
    return result.astimezone(UTC)


def canonical(url):
    parts = urlsplit(url)
    if parts.scheme not in ('https', 'http') or not parts.netloc:
        raise ValueError('Invalid article URL')
    query = urlencode([(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
                       if not key.lower().startswith('utm_') and key.lower() not in ('fbclid', 'gclid')])
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip('/'), query, ''))


def parse_feed(payload, source):
    root = ET.fromstring(payload)
    if root.tag.split('}')[-1] not in ('rss', 'feed', 'RDF'):
        raise ValueError('Not RSS or Atom')
    items = []
    for entry in root.iter():
        if entry.tag.split('}')[-1] not in ('item', 'entry'):
            continue
        fields = {child.tag.split('}')[-1]: child for child in entry}
        try:
            title = html.unescape(''.join(fields['title'].itertext())).strip()
            link = next((child.get('href') for child in entry
                         if child.tag.split('}')[-1] == 'link' and child.get('rel', 'alternate') == 'alternate' and child.get('href')), None)
            if not link:
                link = fields['link'].text
            published = next(fields[key].text for key in ('pubDate', 'published', 'date', 'updated') if key in fields)
            stamp = date(published)
            if not title:
                continue
            items.append(dict(title=title, url=canonical(link), published_at=stamp.isoformat(),
                              source_id=source['id'], publisher=source['publisher'],
                              topic=source['topic'], language=source.get('language')))
        except (KeyError, ValueError, TypeError, StopIteration, AttributeError):
            continue
    return items


def fetch(source):
    request = urllib.request.Request(source['url'], headers={'User-Agent': 'Mozilla/5.0 (compatible; FedericaNews/1.0)', 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'})
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = response.read(5_000_001)
    if len(payload) > 5_000_000:
        raise ValueError('Feed exceeds 5 MB')
    return parse_feed(payload, source)


def refresh(config, previous, now, loader=fetch):
    cutoff = now - timedelta(days=config['freshness_days'])
    candidates, statuses = [], []
    for source in config['sources']:
        old_status = previous.get('sources', {}).get(source['id'], {})
        try:
            entries = loader(source)
            statuses.append((source['id'], dict(status='ok', last_success_at=now.isoformat(), entries=len(entries))))
        except Exception as error:
            print(f"{source['id']}: {type(error).__name__}: {error}", file=sys.stderr)
            entries = [item for item in previous.get('items', []) if item.get('source_id') == source['id']]
            statuses.append((source['id'], dict(status='unavailable', last_success_at=old_status.get('last_success_at'))))
        for item in entries:
            try:
                stamp = date(item['published_at'])
                if cutoff <= stamp <= now:
                    candidates.append({**item, 'url': canonical(item['url'])})
            except (ValueError, TypeError, KeyError):
                continue
    candidates.sort(key=lambda item: date(item['published_at']), reverse=True)
    unique, urls, titles = [], set(), set()
    for item in candidates:
        title = re.sub(r'\W+', ' ', item['title'].casefold()).strip()
        if item['url'] not in urls and title not in titles:
            unique.append(item)
            urls.add(item['url']); titles.add(title)
    selection = []
    for topic in config['topics']:
        pool = [item for item in unique if item['topic'] == topic['id']]
        chosen = []
        if topic['id'] == 'r-python':
            for language in ('R', 'Python'):
                match = next((item for item in pool if item.get('language') == language), None)
                if match:
                    chosen.append(match)
        for item in pool:
            if len(chosen) >= 2:
                break
            if item not in chosen:
                chosen.append(item)
        selection.extend(chosen[:2])
    success = any(status['status'] == 'ok' for _, status in statuses)
    return dict(schema_version=1, checked_at=now.isoformat(),
                last_updated_at=now.isoformat() if success else previous.get('last_updated_at'),
                freshness_days=config['freshness_days'], topics=config['topics'],
                sources=dict(statuses), items=selection)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'data/news.json')
    args = parser.parse_args()
    config = json.loads((ROOT / 'data/news-feeds.json').read_text())
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    result = refresh(config, previous, datetime.now(UTC))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(args.output)
    print(f"Selected {len(result['items'])} headlines; {sum(s['status']=='ok' for s in result['sources'].values())} feeds available")

if __name__ == '__main__':
    main()
