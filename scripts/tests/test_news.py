import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location('news', Path(__file__).parents[1] / 'update-news.py')
news = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news)
NOW = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
SOURCE = dict(id='r', publisher='R Project', topic='r-python', language='R')
CONFIG = dict(freshness_days=45, topics=[dict(id='r-python', title='R & Python')], sources=[SOURCE])

def item(title='One', published='2026-10-19T00:00:00+00:00', **extra):
    return dict(title=title, published_at=published, url='https://example.org/' + title, source_id='r', publisher='R Project', topic='r-python', language='R', **extra)

class NewsTests(unittest.TestCase):
    def test_rss_atom_dates(self):
        rss = b'<rss><channel><item><title>A &amp; B</title><link>https://example.org/a</link><pubDate>Mon, 19 Oct 2026 10:00:00 GMT</pubDate></item><item><title>Bad</title></item></channel></rss>'
        self.assertEqual(news.parse_feed(rss, SOURCE)[0]['title'], 'A & B')
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Atom</title><link rel="self" href="https://example.org/feed"/><link href="https://example.org/article"/><published>2026-10-18T10:00:00Z</published></entry></feed>'
        self.assertEqual(news.parse_feed(atom, SOURCE)[0]['url'], 'https://example.org/article')
        with self.assertRaises(ValueError): news.parse_feed(b'<html/>', SOURCE)
        with self.assertRaises(Exception): news.parse_feed(b'<rss>', SOURCE)
        with self.assertRaises(ValueError): news.date('2026-10-19')

    def test_tracking_fragments_and_unsafe_urls(self):
        self.assertEqual(news.canonical('https://example.org/a/?utm_source=rss#top'), 'https://example.org/a')
        with self.assertRaises(ValueError): news.canonical('javascript:alert(1)')

    def test_partial_failure_retains_only_failed_source(self):
        other = dict(id='py', publisher='PSF', topic='r-python', language='Python')
        config = {**CONFIG, 'sources': [SOURCE, other]}
        previous = dict(items=[item(), {**item('Prior Python'), 'source_id': 'py', 'language': 'Python'}])
        def load(source):
            if source['id'] == 'r': raise OSError('offline')
            return []
        result = news.refresh(config, previous, NOW, load)
        self.assertEqual([x['title'] for x in result['items']], ['One'])
        self.assertEqual(result['last_updated_at'], NOW.isoformat())

    def test_dates_duplicates_and_replacement(self):
        entries = [item(), item(), item('Future', '2026-10-21T00:00:00Z'), item('Old', '2025-01-01T00:00:00Z'), item('Invalid', 'bad')]
        result = news.refresh(CONFIG, {'items': [item('Previous')]}, NOW, lambda _: entries)
        self.assertEqual([x['title'] for x in result['items']], ['One'])
        self.assertEqual(news.refresh(CONFIG, result, NOW, lambda _: [])['items'], [])
        same_title = {**item(), 'url': 'https://example.org/other'}
        self.assertEqual(len(news.refresh(CONFIG, {}, NOW, lambda _: [item(), same_title])['items']), 1)

    def test_failure_cache_expires_and_timestamp_is_honest(self):
        def fail(_): raise OSError('offline')
        previous = dict(items=[item(), item('Old', '2025-01-01T00:00:00Z')], last_updated_at='2026-10-19T12:00:00Z', sources={})
        result = news.refresh(CONFIG, previous, NOW, fail)
        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['last_updated_at'], previous['last_updated_at'])
        self.assertEqual(result['sources']['r']['status'], 'unavailable')
        later = NOW.replace(year=2027)
        self.assertEqual(news.refresh(CONFIG, result, later, fail)['items'], [])

    def test_r_and_python_each_get_a_place(self):
        python = dict(id='py', publisher='PSF', topic='r-python', language='Python')
        config = {**CONFIG, 'sources': [SOURCE, python]}
        def load(source):
            if source['id'] == 'py': return [{**item('Python'), 'source_id': 'py', 'language': 'Python'}]
            return [item('New R'), item('Another R')]
        result = news.refresh(config, {}, NOW, load)
        self.assertEqual({x['language'] for x in result['items']}, {'R', 'Python'})
        self.assertEqual(len(result['items']), 2)

if __name__ == '__main__': unittest.main()
