import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sync_workshops', Path(__file__).parents[1] / 'sync-workshops.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

RECAP = 'talks/2026/meetup/10232026_federicagazzelloni.qmd'
DOCUMENT = '''---
title: "Machine Learning — Part 2"
date: 2026-10-23
description: "Fit and evaluate a neural network."
teaching:
  presenters:
    - id: fgazzelloni
      role: presenter
  kind: workshop
  topic: "AI & machine learning"
  materials:
    - label: "Code"
      url: "https://github.com/fgazzelloni/example"
---
{{< video https://youtu.be/Zi4eCdxLLIo >}}
'''
BODY = '''<p class="workshop-results">1 sessions · 1 recordings · newest first</p>
  <div class="workshop-grid">
<article class="workshop-card"><a class="workshop-thumbnail" href="https://youtu.be/v8bx-BYvIZo"></a>Legacy abstract</article>
  </div>
'''


class WorkshopTests(unittest.TestCase):
    def event(self):
        return sync.event_from_recap(RECAP, DOCUMENT)

    def test_attribution_is_explicit_not_author_or_filename(self):
        self.assertEqual(self.event()['recording_url'], 'https://youtu.be/Zi4eCdxLLIo')
        self.assertEqual(self.event()['date'], '2026-10-23')
        self.assertIsNone(sync.event_from_recap(RECAP, DOCUMENT.replace('id: fgazzelloni', 'id: guest')))
        self.assertIsNone(sync.event_from_recap(RECAP, DOCUMENT.replace('role: presenter', 'role: host')))
        self.assertIsNone(sync.event_from_recap(RECAP, '---\nauthor: Federica Gazzelloni\n---\nGuest talk'))
        co = DOCUMENT.replace('role: presenter', 'role: co-instructor')
        self.assertEqual(sync.event_from_recap(RECAP, co)['role'], 'co-instructor')

    def test_upsert_updates_recording_without_duplicating(self):
        old = self.event()
        old['recording_url'] = None
        previous = dict(schema_version=1, events=[old])
        merged = sync.merge_events(previous, [self.event()])
        self.assertEqual(len(merged['events']), 1)
        self.assertEqual(merged['events'][0]['recording_url'], self.event()['recording_url'])

    def test_missing_sources_do_not_delete_and_duplicate_urls_fail(self):
        previous = dict(schema_version=1, events=[self.event()])
        self.assertEqual(sync.merge_events(previous, []), previous)
        with self.assertRaises(ValueError):
            sync.merge_events(previous, [self.event(), self.event()])

    def test_render_is_repeatable_and_preserves_legacy(self):
        rendered = sync.render_body(BODY, [self.event()])
        self.assertEqual(rendered, sync.render_body(rendered, [self.event()]))
        self.assertIn('Legacy abstract', rendered)
        self.assertIn('2 sessions · 2 recordings', rendered)
        self.assertEqual(rendered.count('data-event-id='), 1)

    def test_legacy_duplicate_detected_by_video_or_recap(self):
        body = BODY.replace('v8bx-BYvIZo', 'Zi4eCdxLLIo')
        self.assertNotIn('data-event-id=', sync.render_body(body, [self.event()]))
        body = BODY.replace('Legacy abstract', self.event()['recap_url'])
        self.assertNotIn('data-event-id=', sync.render_body(body, [self.event()]))

    def test_materials_only_session_can_later_gain_recording(self):
        e = self.event()
        e['recording_url'] = None
        page = sync.render_body(BODY, [e])
        self.assertIn('2 sessions · 1 recordings', page)
        self.assertNotIn('i.ytimg.com', page)
        self.assertIn('2 sessions · 2 recordings', sync.render_body(page, [self.event()]))

    def test_unsafe_urls_and_invalid_dates_fail(self):
        for key, value in [('recap_url', 'javascript:alert(1)'), ('recording_url', 'https://evil.example/Zi4eCdxLLIo'), ('date', '2026-02-30')]:
            e = self.event()
            e[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                sync.validate(e)
        e = self.event()
        e['materials'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            sync.validate(e)

    def test_text_is_html_escaped(self):
        e = self.event()
        e['title'] = '<script>bad()</script> & "title"'
        e['summary'] = '<img src=x onerror=bad()>'
        rendered = sync.card(e)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('&lt;img', rendered)

    def test_recap_cover_is_used_when_available(self):
        doc = DOCUMENT.replace('description:', 'image: "https://example.org/cover.webp"\ndescription:')
        event = sync.event_from_recap(RECAP, doc)
        self.assertIn('src="https://example.org/cover.webp"', sync.card(event))
        event['image_url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            sync.validate(event)

    def test_ambiguous_recordings_require_explicit_choice(self):
        extra = DOCUMENT + '\n{{< video https://youtu.be/v8bx-BYvIZo >}}'
        with self.assertRaises(ValueError):
            sync.event_from_recap(RECAP, extra)

    def test_bad_marker_prevents_writing_register(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'about/rladies').mkdir(parents=True)
            register = root / 'data/teaching-events.json'
            register.write_text('{"schema_version": 1, "events": []}\n')
            (root / 'about/rladies/_rladies-body.qmd').write_text('Missing grid')
            original = register.read_bytes()
            with self.assertRaises(ValueError):
                sync.sync(root, [(RECAP, DOCUMENT)])
            self.assertEqual(register.read_bytes(), original)

    def test_future_session_is_not_imported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'about/rladies').mkdir(parents=True)
            (root / 'data/teaching-events.json').write_text('{"schema_version": 1, "events": []}\n')
            (root / 'about/rladies/_rladies-body.qmd').write_text(BODY)
            incoming, _ = sync.sync(root, [(RECAP, DOCUMENT.replace('2026-10-23', '2099-10-23'))])
            self.assertEqual(incoming, [])

    def test_unpublished_or_unavailable_recap_leaves_files_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'about/rladies').mkdir(parents=True)
            register = root / 'data/teaching-events.json'
            body = root / 'about/rladies/_rladies-body.qmd'
            register.write_text('{"schema_version": 1, "events": []}\n')
            body.write_text(BODY)
            before = (register.read_bytes(), body.read_bytes())
            for failure in (OSError('offline'), None):
                with patch.object(sync, 'get_text', side_effect=failure, return_value='Not published'):
                    with self.assertRaises((OSError, ValueError)):
                        sync.sync(root, [(RECAP, DOCUMENT)], verify_published=True)
                self.assertEqual((register.read_bytes(), body.read_bytes()), before)


if __name__ == '__main__':
    unittest.main()
