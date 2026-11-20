import threading
import time
import unittest

from scanner import FuturesScanner
from test_scanner import FakeExchange


class ProgressiveTests(unittest.TestCase):
 def test_stale_individual_result_is_not_exposed(self):
  scan=FuturesScanner(factory=FakeExchange)
  scan.data.update(last_scan=time.time(),results=[{'symbol':'BTC/USDT:USDT','checked_at':time.time()-901,'last_candle':time.time()-3700}])
  self.assertEqual(scan.get()['results'],[])

 def test_catalog_is_cached_between_scans(self):
  class CountingExchange(FakeExchange):
   calls=0
   def load_markets(self):
    CountingExchange.calls+=1
    return super().load_markets()
  scan=FuturesScanner(factory=CountingExchange); scan.symbols=['BTC/USDT:USDT']
  scan.run_once(); scan.run_once()
  self.assertEqual(CountingExchange.calls,1)

 def test_results_visible_before_cycle_finishes_and_new_focus_wins(self):
  waiting=threading.Event(); release=threading.Event()
  class SlowExchange(FakeExchange):
   def load_markets(self):
    return {symbol:{'swap':True,'linear':True,'settle':'USDT','active':True} for symbol in ['BTC/USDT:USDT','ETH/USDT:USDT']}
   def fetch_ohlcv(self,symbol,*args,**kwargs):
    if symbol.startswith('ETH'): waiting.set(); release.wait(3)
    return super().fetch_ohlcv(symbol,*args,**kwargs)
  scan=FuturesScanner(factory=SlowExchange); scan.symbols=['BTC/USDT:USDT','ETH/USDT:USDT']
  worker=threading.Thread(target=scan.run_once); worker.start()
  try:
   self.assertTrue(waiting.wait(3))
   self.assertEqual(scan.get()['results'][0]['symbol'],'BTC/USDT:USDT')
   scan.request_analysis('ETH/USDT:USDT')
  finally:
   release.set(); worker.join(5)
  self.assertFalse(worker.is_alive())
  self.assertEqual(scan.get()['results'],[])
  self.assertEqual(scan.get()['focus'],'ETH/USDT:USDT')
