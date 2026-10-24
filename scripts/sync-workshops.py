#!/usr/bin/env python3
"""Import explicitly attributed teaching recaps and regenerate workshop cards.

No publication, model calls, or credentials are needed for a local import.
Run with --source-dir to use a local R-Ladies Rome checkout.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import escape, unescape
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import urlsplit, parse_qs
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = 'rladies/website-italy-rladiesrome'
START = '<!-- BEGIN IMPORTED TEACHING EVENTS -->'
END = '<!-- END IMPORTED TEACHING EVENTS -->'
TOPICS = {
    'AI & machine learning', 'Community', 'Data visualisation', 'Data wrangling',
    'Health modelling', 'Python', 'Quarto', 'R fundamentals',
    'Reproducible workflows', 'Spatial analysis',
}
ROLES = {'presenter', 'co-instructor'}


def get_text(url):
    req = Request(url, headers={'User-Agent': 'Federica-workshop-importer/1.0'})
    with urlopen(req, timeout=30) as response:
        return response.read(4_000_001).decode('utf-8')


def source_documents(source_dir=None):
    if source_dir:
        root = Path(source_dir)
        return [(p.relative_to(root).as_posix(), p.read_text())
                for p in sorted((root / 'talks').rglob('*.qmd'))]
    # Resolve main once, then fetch every file at that immutable commit.
    tree = json.loads(get_text(f'https://api.github.com/repos/{REPO}/git/trees/main?recursive=1'))
    if tree.get('truncated') or not tree.get('sha') or not isinstance(tree.get('tree'), list):
        raise ValueError('Incomplete source tree; existing cards have not been changed.')
    paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob'
             and x['path'].startswith('talks/') and x['path'].endswith('.qmd')]
    if not paths:
        raise ValueError('No recap sources found; existing cards have not been changed.')
    def read(path):
        return path, get_text(f'https://raw.githubusercontent.com/{REPO}/{tree["sha"]}/{path}')
    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(read, sorted(paths)))


def safe_url(value):
    if not isinstance(value, str):
        raise ValueError('Links must be strings.')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f'Expected a public HTTPS link: {value!r}')
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Whitespace is not allowed in links.')
    return value


def video_id(url):
    parsed = urlsplit(safe_url(url))
    if parsed.hostname == 'youtu.be':
        value = parsed.path.lstrip('/')
    elif parsed.hostname in {'youtube.com', 'www.youtube.com'} and parsed.path == '/watch':
        value = parse_qs(parsed.query).get('v', [''])[0]
    else:
        raise ValueError('Recording must be a YouTube watch or youtu.be link.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', value):
        raise ValueError('Invalid YouTube recording ID.')
    return value


def validate(event):
    for field in ('id', 'title', 'date', 'host', 'kind', 'role', 'topic', 'summary', 'recap_url', 'source'):
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f'Missing or invalid event field: {field}')
    date.fromisoformat(event['date'])
    if event['role'] not in ROLES or event['kind'] not in {'workshop', 'talk', 'tutorial'}:
        raise ValueError('Unsupported teaching role or session type.')
    if event['topic'] not in TOPICS:
        raise ValueError('Choose a topic already supported by the workshop filter.')
    if event['id'] != safe_url(event['recap_url']):
        raise ValueError('The event ID must be its canonical recap URL.')
    if event.get('recording_url'):
        video_id(event['recording_url'])
    if event.get('image_url'):
        safe_url(event['image_url'])
    if not isinstance(event.get('materials', []), list):
        raise ValueError('Materials must be a list of labelled links.')
    for link in event.get('materials', []):
        if not isinstance(link, dict) or not isinstance(link.get('label'), str) or not link['label'].strip():
            raise ValueError('Each material needs a label and URL.')
        safe_url(link['url'])
    return event


def event_from_recap(path, content):
    parts = content.split('---', 2)
    if len(parts) < 3 or parts[0].strip():
        return None
    if not re.search(r'^teaching:\s*', parts[1], re.MULTILINE):
        return None
    metadata = yaml.safe_load(parts[1]) or {}
    teaching = metadata.get('teaching')
    if teaching is None:
        return None
    if not isinstance(teaching, dict) or not isinstance(teaching.get('presenters'), list):
        raise ValueError(f'{path}: teaching metadata needs a presenters list.')
    people = [p for p in teaching['presenters'] if isinstance(p, dict)
              and p.get('id') == 'fgazzelloni' and p.get('role') in ROLES]
    if not people:
        return None
    relative = PurePosixPath(path)
    if relative.is_absolute() or '..' in relative.parts or not path.startswith('talks/'):
        raise ValueError('Invalid recap path.')
    recap = 'https://rladiesrome.org/' + str(relative.with_suffix('.html'))
    recordings = re.findall(r'\{\{<\s*video\s+(https://[^\s>]+)\s*>\}\}', parts[2])
    recording = teaching.get('recording_url')
    if recording is None:
        if len(recordings) > 1:
            raise ValueError(f'{path}: choose teaching.recording_url explicitly.')
        recording = recordings[0] if recordings else None
    event = dict(id=recap, title=metadata['title'], date=str(metadata['date']),
                 host='R-Ladies Rome', kind=teaching['kind'], role=people[0]['role'],
                 topic=teaching['topic'], summary=teaching.get('summary', metadata.get('description')),
                 recap_url=recap, source=REPO, recording_url=recording,
                 materials=teaching.get('materials', []))
    if isinstance(metadata.get('image'), str) and metadata['image'].startswith('https://'):
        event['image_url'] = metadata['image']
    return validate(event)


def merge_events(previous, incoming):
    if previous.get('schema_version') != 1 or not isinstance(previous.get('events'), list):
        raise ValueError('Unsupported teaching register format.')
    result = {}
    for group in (previous['events'], incoming):
        seen = set()
        for event in group:
            validate(event)
            if event['id'] in seen:
                raise ValueError('Duplicate recap URL in event register or source.')
            seen.add(event['id'])
            result[event['id']] = event
    # Missing source entries are retained: absence is not permission to delete.
    return dict(schema_version=1, events=sorted(result.values(), key=lambda e: (e['date'], e['id']), reverse=True))


def card(event):
    e = {k: escape(str(v), quote=True) for k, v in event.items() if k != 'materials'}
    links = [dict(label='Event recap and resources', url=event['recap_url'])] + event.get('materials', [])
    resource_list = '\n'.join(f'        <li><a href="{escape(x["url"], quote=True)}">{escape(x["label"])}</a></li>' for x in links)
    image = ''
    action = ''
    if event.get('recording_url'):
        vid = video_id(event['recording_url'])
        thumbnail = escape(event.get('image_url') or f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg', quote=True)
        image = f'''  <a class="workshop-thumbnail" href="{e['recording_url']}" aria-label="Watch {e['title']} on YouTube">
    <img src="{thumbnail}" alt="" loading="lazy" width="480" height="360" />
    <span class="workshop-play" aria-hidden="true">▶</span>
    <span class="workshop-watch-label">Watch recording</span>
  </a>\n'''
        action = f'      <a class="workshop-watch" href="{e["recording_url"]}">Watch on YouTube <span aria-hidden="true">↗</span></a>\n'
    day = date.fromisoformat(event['date'])
    display_date = f'{day.day} {day.strftime("%B %Y")}'
    return f'''<article class="workshop-card" data-topic="{e['topic']}" data-event-id="{e['id']}">
{image}  <div class="workshop-card__body">
    <span class="workshop-tag">{e['topic']}</span>
    <h3>{e['title']}</h3>
    <p class="workshop-meta"><time datetime="{e['date']}">{display_date}</time> · {e['host']}</p>
    <details class="workshop-details">
      <summary>Session details &amp; materials</summary>
      <p>{e['summary']}</p>
      <ul>
{resource_list}
      </ul>
    </details>
    <div class="workshop-card-actions">
{action}      <a class="workshop-materials" href="{e['recap_url']}">Recap &amp; materials</a>
    </div>
  </div>
</article>'''


def render_body(body, events):
    if START not in body and END not in body:
        anchor = '  <div class="workshop-grid">\n'
        if body.count(anchor) != 1:
            raise ValueError('Cannot locate the existing workshop grid.')
        body = body.replace(anchor, anchor + START + '\n' + END + '\n', 1)
    if body.count(START) != 1 or body.count(END) != 1:
        raise ValueError('Generated card markers are missing or duplicated.')
    before, rest = body.split(START, 1)
    _, after = rest.split(END, 1)
    legacy = before + after
    new_cards = []
    for event in events:
        # Existing hand-written cards stay intact, including their abstracts.
        if event['id'] in legacy:
            continue
        if event.get('recording_url') and video_id(event['recording_url']) in legacy:
            continue
        new_cards.append(card(event))
    generated = '\n\n'.join(new_cards)
    result = before + START + '\n' + generated + '\n' + END + after
    count = len(re.findall(r'<article class="workshop-card"', result))
    recordings = len(re.findall(r'<a class="workshop-thumbnail"', result))
    return re.sub(r'\d+ sessions · \d+ recordings · newest first',
                  f'{count} sessions · {recordings} recordings · newest first', result)


def sync(root, documents, verify_published=False):
    register = root / 'data/teaching-events.json'
    target = root / 'about/rladies/_rladies-body.qmd'
    previous = json.loads(register.read_text())
    incoming = [e for path, source in documents if (e := event_from_recap(path, source))
                and date.fromisoformat(e['date']) <= date.today()]
    if verify_published:
        for event in incoming:
            if event['title'] not in unescape(get_text(event['recap_url'])):
                raise ValueError(f'Recap is not yet available with the expected title: {event["recap_url"]}')
    merged = merge_events(previous, incoming)
    new_json = json.dumps(merged, ensure_ascii=False, indent=2) + '\n'
    new_body = render_body(target.read_text(), merged['events'])
    # All inputs are read and validated before either output is touched.
    changed = []
    for path, content in ((register, new_json), (target, new_body)):
        if path.read_text() != content:
            path.write_text(content)
            changed.append(str(path.relative_to(root)))
    return incoming, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--source-dir', type=Path, help='Local R-Ladies Rome checkout; otherwise read public main')
    args = parser.parse_args()
    try:
        incoming, changed = sync(args.root, source_documents(args.source_dir), verify_published=not args.source_dir)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f'Workshop import failed: {exc}', file=sys.stderr)
        return 1
    print(f'{len(incoming)} eligible recap(s); ' + (', '.join(changed) if changed else 'no changes'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
