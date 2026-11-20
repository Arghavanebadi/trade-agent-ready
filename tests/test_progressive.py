import threading
import time
import unittest
from unittest.mock import patch

from scanner import FuturesScanner
from test_scanner import FakeExchange, sample
import research


class ProgressiveTests(unittest.TestCase):
 def setUp(self):
  audit=patch('scanner.Audit'); audit.start(); self.addCleanup(audit.stop)
 def test_low_price_agent_evidence_preserves_precision(self):
  rows=sample()
  for row in rows:
   for field in ('open','high','low','close'): row[field]*=0.00000001
  result=research.evaluate(rows,now=time.time())
  self.assertTrue(result['valid'])
  for name in ('Trend architect','Breakout watcher','Mean reversion','VWAP analyst'):
   agent=next(agent for agent in result['agents'] if agent['name']==name)
   self.assertNotIn('0.00 /',agent['detail'])
   self.assertNotIn('· 0.00',agent['detail'])

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

 def test_role_results_are_published_only_after_validated_analysis(self):
  waiting=threading.Event(); release=threading.Event()
  class SlowSupplement(FakeExchange):
   def fetch_funding_rate(self,symbol):
    waiting.set(); release.wait(3)
    return super().fetch_funding_rate(symbol)
  scan=FuturesScanner(factory=SlowSupplement); scan.symbols=['BTC/USDT:USDT']
  scan.request_analysis('BTC/USDT:USDT')
  worker=threading.Thread(target=scan.run_once); worker.start()
  try:
   self.assertTrue(waiting.wait(3)); progress=scan.get()['progress']
   self.assertEqual(progress['stage'],'enriching'); self.assertEqual(progress['symbol'],'BTC/USDT:USDT')
   self.assertEqual(len(progress['agents']),15); self.assertEqual(scan.get()['results'],[])
   scan.request_analysis('BTC/USDT:USDT')
   self.assertEqual(scan.get()['progress']['agents'],[])
  finally:
   release.set(); worker.join(5)
  self.assertFalse(worker.is_alive()); self.assertEqual(scan.get()['results'],[])

 def test_partial_role_results_expire_with_their_source_candle(self):
  scan=FuturesScanner(factory=FakeExchange)
  scan.data['progress']={'symbol':'BTC/USDT:USDT','stage':'enriching','agents':[{'role':'test'}], 'agents_at':time.time(),'last_candle':time.time()-10000}
  self.assertEqual(scan.get()['progress']['agents'],[])
