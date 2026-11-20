import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from scanner import CATALOG_MAX_AGE, FuturesScanner, read_catalog, write_catalog
from test_scanner import FakeExchange


class CatalogCacheTests(unittest.TestCase):
 def test_cache_round_trip_expiration_and_provider(self):
  with tempfile.TemporaryDirectory() as directory:
   path=Path(directory)/'catalog.json'; now=time.time()
   write_catalog(path,'market-a',FakeExchange().load_markets(),now)
   markets,stamp=read_catalog(path,'market-a',now+10)
   self.assertIn('BTC/USDT:USDT',markets); self.assertEqual(stamp,now)
   self.assertIsNone(read_catalog(path,'market-b',now+10))
   self.assertIsNone(read_catalog(path,'market-a',now+CATALOG_MAX_AGE+1))
   path.write_text('{broken',encoding='utf-8')
   self.assertIsNone(read_catalog(path,'market-a',now+10))

 def test_unavailable_catalog_uses_recent_verified_cache(self):
  class UnavailableCatalog(FakeExchange):
   def load_markets(self): raise RuntimeError('HTTP Error 403')
  scan=FuturesScanner(factory=UnavailableCatalog); scan.symbols=['BTC/USDT:USDT']
  scan.market_cache=FakeExchange().load_markets(); scan.market_cache_checked_at=time.time()-600
  with patch('scanner.Audit'): result=scan.run_once()
  self.assertEqual(result['status'],'running'); self.assertEqual(len(result['results'][0]['agents']),15)
  self.assertEqual(scan.get()['catalog_status'],'cached')

 def test_expired_catalog_does_not_enable_analysis(self):
  class UnavailableCatalog(FakeExchange):
   def load_markets(self): raise RuntimeError('HTTP Error 403')
  scan=FuturesScanner(factory=UnavailableCatalog); scan.symbols=['BTC/USDT:USDT']
  scan.market_cache=FakeExchange().load_markets(); scan.market_cache_checked_at=time.time()-CATALOG_MAX_AGE-1
  with patch('scanner.Audit'): result=scan.run_once()
  self.assertEqual(result['status'],'error'); self.assertEqual(result['results'],[])
  self.assertEqual(scan.get()['catalog_status'],'unavailable')


if __name__=='__main__': unittest.main()
