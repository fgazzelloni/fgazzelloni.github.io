#!/usr/bin/env python3
"""Check the teaching register against the two rendered workshop pages."""
from html import unescape
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
events = json.loads((root / 'data/teaching-events.json').read_text())['events']
for relative in ('about/workshops/index.html', 'about/rladies/index.html'):
    page = unescape((root / '_site' / relative).read_text())
    for event in events:
        assert event['title'] in page, f'{relative}: missing title'
        assert event['recap_url'] in page, f'{relative}: missing recap'
        if event.get('recording_url'):
            assert event['recording_url'] in page, f'{relative}: missing recording'
    assert 'workshop-filters.js' in page, f'{relative}: missing search and filters'
print(f'PASS: {len(events)} teaching event(s) present on both rendered pages.')
