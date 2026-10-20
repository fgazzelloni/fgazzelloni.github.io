import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location('render_news', Path(__file__).resolve().parents[1] / 'render-news.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RenderNewsTests(unittest.TestCase):
    def test_static_headlines_escape_content_and_exclude_unsafe_or_expired_links(self):
        data = dict(freshness_days=45, topics=[dict(id='r', title='R & Python')], items=[
            dict(topic='r', title='<New tools>', publisher='A & B', published_at='2026-10-19T00:00:00+00:00', url='https://example.org/?a=1&b=2'),
            dict(topic='r', title='Unsafe', publisher='X', published_at='2026-10-19T00:00:00+00:00', url='javascript:alert(1)'),
            dict(topic='r', title='Expired', publisher='X', published_at='2020-01-01T00:00:00+00:00', url='https://example.org/old'),
        ])
        result = module.render(data, datetime(2026, 10, 20, tzinfo=timezone.utc))
        self.assertIn('&lt;New tools&gt;', result)
        self.assertIn('R &amp; Python', result)
        self.assertIn('a=1&amp;b=2', result)
        self.assertNotIn('Unsafe', result)
        self.assertNotIn('Expired', result)
