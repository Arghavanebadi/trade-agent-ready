import io
import json
import threading
import unittest
from unittest.mock import patch
import news_digest

FEED = b'''<rss><channel><item><title>Missile attack reported</title><link>https://www.bbc.com/news/example</link><pubDate>Thu, 19 Nov 2026 12:00:00 GMT</pubDate></item><item><title>Invalid link</title><link>https://evil.test/news</link><pubDate>Thu, 19 Nov 2026 12:00:00 GMT</pubDate></item></channel></rss>'''

class NewsDigestTests(unittest.TestCase):
    def test_feed_validates_links_dates_and_flags(self):
        items = news_digest.parse_feed(FEED,'BBC',('bbc.com',),1795093200)
        self.assertEqual(len(items),1)
        self.assertTrue(items[0]['critical'])
        self.assertIsNone(items[0]['summary'])

    def test_unsafe_xml_rejected(self):
        with self.assertRaises(ValueError):
            news_digest.parse_feed(b'<!DOCTYPE x><rss/>','BBC',('bbc.com',),0)

    def test_summary_only_uses_supplied_headline(self):
        entries = [{'title':'Example','source':'BBC','summary':None,'impact':None}]
        response = {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps([{'id':0,'summary':'خبر تازه','impact':'اثر نامشخص'}])}]}]}
        with patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(response).encode())):
            news_digest.summarize(entries,'test')
        self.assertEqual(entries[0]['summary'],'خبر تازه')

    def test_failure_marks_cached_news_unavailable(self):
        monitor = news_digest.NewsMonitor()
        monitor.state['items'] = [{'title':'cached'}]
        with patch('urllib.request.urlopen',side_effect=OSError('offline')):
            monitor.refresh()
        self.assertEqual(monitor.get()['status'],'unavailable')
        self.assertEqual(monitor.get()['items'][0]['title'],'cached')

    def test_malformed_model_response_keeps_valid_news_available(self):
        malformed = json.dumps({'status':'completed','output':['invalid message']}).encode()
        with patch.object(news_digest,'SOURCES',(('BBC','https://feed.example/rss',('bbc.com',)),)), patch('news_digest.time.time',return_value=1795093200), patch.dict('os.environ',{'NEWS_AI_SUMMARY':'1','XAI_API_KEY':'test'}), patch('urllib.request.urlopen',side_effect=[io.BytesIO(FEED),io.BytesIO(malformed)]):
            monitor=news_digest.NewsMonitor()
            monitor.refresh()
            result=monitor.get()
        self.assertEqual(result['status'],'online')
        self.assertEqual(result['ai_status'],'unavailable')
        self.assertEqual(len(result['items']),1)
        self.assertIsNone(result['items'][0]['summary'])

    def test_invalid_link_does_not_discard_other_articles(self):
        bad = b'<item><title>Bad</title><link>https://[invalid</link><pubDate>Thu, 19 Nov 2026 12:00:00 GMT</pubDate></item>'
        articles=news_digest.parse_feed(FEED.replace(b'</channel>',bad+b'</channel>'),'BBC',('bbc.com',),1795093200)
        self.assertEqual(len(articles),1)

    def test_start_does_not_duplicate_worker(self):
        monitor=news_digest.NewsMonitor()
        started=threading.Event()
        with patch.object(monitor,'refresh',side_effect=started.set):
            monitor.start()
            self.assertTrue(started.wait(2))
            worker=monitor.thread
            monitor.start()
            self.assertIs(monitor.thread,worker)
            monitor.stop()
            worker.join(2)
        self.assertFalse(worker.is_alive())
