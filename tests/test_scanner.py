import copy, math, time, unittest
from unittest.mock import patch
import research
from scanner import FuturesScanner

def sample():
 now=int(time.time()//3600)*3600
 rows=[]
 for i in range(120):
  price=100+i*.2+math.sin(i)*.1
  rows.append({'time':now-(120-i)*3600,'open':price-.1,'high':price+.3,'low':price-.3,'close':price,'volume':100+i})
 return rows
class FakeExchange:
 has={'fetchFundingRate':True,'fetchOpenInterest':True}
 def load_markets(self): return {'BTC/USDT:USDT':{'swap':True,'linear':True,'settle':'USDT','active':True}}
 def fetch_ohlcv(self,*args,**kwargs): return [[r['time']*1000,r['open'],r['high'],r['low'],r['close'],r['volume']] for r in sample()]
 def fetch_funding_rate(self,s): return {'fundingRate':.0001}
 def fetch_open_interest(self,s): return {'openInterestAmount':42}
class Tests(unittest.TestCase):
 def setUp(self):
  audit=patch('scanner.Audit'); audit.start(); self.addCleanup(audit.stop)
 def test_roles_and_data_validation(self):
  rows=sample();result=research.evaluate(rows,now=time.time());self.assertTrue(result['valid']);self.assertEqual(len(result['agents']),15)
  rows[-1]['close']=float('nan');self.assertFalse(research.evaluate(rows)['valid'])
 def test_gap_and_stale(self):
  rows=sample();rows[-1]['time']-=3600;self.assertFalse(research.evaluate(rows)['valid'])
  self.assertFalse(research.evaluate(sample(),now=time.time()+86400)['valid'])
 def test_malformed_values_fail_closed(self):
  for field,value in [('close','100'),('volume',True),('time','bad'),('time',float('nan')),('time',123)]:
   rows=sample(); rows[-1][field]=value
   with self.subTest(field=field,value=value):
    result=research.evaluate(rows,now=time.time()); self.assertFalse(result['valid']); self.assertEqual(result['agents'],[])
  self.assertFalse(research.evaluate(None,now=time.time())['valid'])
 def test_scanner_contract_filter_and_metrics(self):
  scan=FuturesScanner(factory=FakeExchange);scan.symbols=['BTC/USDT:USDT','BAD/USDT:USDT'];result=scan.run_once()
  self.assertEqual(result['status'],'running');self.assertEqual(len(result['results']),1);self.assertEqual(len(result['errors']),1);self.assertEqual(result['results'][0]['funding_rate'],.0001);self.assertEqual(result['results'][0]['open_interest'],42)
 def test_scanner_stale_clears_selection(self):
  scan=FuturesScanner(factory=FakeExchange);scan.data.update(status='running',last_scan=time.time()-3600,selected={'symbol':'BTC'})
  self.assertEqual(scan.get()['status'],'stale');self.assertIsNone(scan.get()['selected'])
 def test_provider_failure_never_produces_signal(self):
  def fail(): raise RuntimeError('unavailable')
  scan=FuturesScanner(factory=fail);r=scan.run_once();self.assertEqual(r['status'],'error');self.assertIsNone(r['selected'])
  state=scan.get();self.assertEqual(len(state['agents']),15);self.assertTrue(all(a['status']=='بدون داده' for a in state['agents']));self.assertTrue(any(e['level']=='error' for e in state['activity']))
 def test_progress_and_agent_results(self):
  scan=FuturesScanner(factory=FakeExchange);scan.symbols=['BTC/USDT:USDT'];scan.run_once();state=scan.get()
  self.assertEqual(state['progress']['completed'],1);self.assertEqual(len(state['agents']),15)
  self.assertEqual(next(a for a in state['agents'] if a['name']=='Stochastic analyst')['role'],'استوکاستیک')
  candles=state['results'][0]['candles']
  self.assertEqual(len(candles),60)
  self.assertEqual(candles[-1]['time'],state['results'][0]['last_candle'])
  self.assertLessEqual(candles[-1]['time']+3600,time.time())
 def test_request_focus_and_result(self):
  scan=FuturesScanner(factory=FakeExchange);scan.symbols=['BTC/USDT:USDT'];scan.request_analysis('BTC/USDT:USDT')
  self.assertIsNone(scan.get()['selected']);scan.run_once();state=scan.get()
  self.assertEqual(state['selected']['symbol'],'BTC/USDT:USDT');self.assertEqual(len(state['agents']),15)
  with self.assertRaises(ValueError): scan.request_analysis('INVALID')
 def test_incomplete_candle_is_not_used(self):
  rows=sample(); now=time.time(); rows[-1]['time']=int(now//3600)*3600
  self.assertFalse(research.evaluate(rows,now=now)['valid'])
 def test_high_volume_with_flat_return_has_no_directional_vote(self):
  rows=sample(); price=rows[-6]['close']
  rows[-1].update(open=price,high=price+.3,low=price-.3,close=price,volume=10000)
  result=research.evaluate(rows,now=time.time())
  agent=next(agent for agent in result['agents'] if agent['name']=='Volume analyst')
  self.assertEqual(agent['status'],'بالا'); self.assertEqual(agent['vote'],0)
 def test_optional_analysis_failures_preserve_valid_market_report(self):
  scan=FuturesScanner(); scan.symbols=['BTC/USDT:USDT']
  with patch.object(scan,'client',return_value=FakeExchange()), patch('scanner.diagnostics.evaluate_votes',side_effect=RuntimeError('diagnostics failed')), patch('scanner.headlines.fetch',return_value=[]), patch('scanner.headlines.feature',side_effect=RuntimeError('news failed')), patch('scanner.learner.observe',side_effect=RuntimeError('database failed')):
   result=scan.run_once()
  self.assertEqual(result['status'],'running'); report=result['results'][0]
  self.assertEqual(len(report['agents']),15); self.assertIsNone(report['diagnostics'])
  self.assertFalse(report['news']['available'])
  self.assertTrue({'diagnostics','news','adaptive'}.issubset(report['missing']))
  self.assertTrue(any(event['level']=='error' for event in scan.get()['activity']))
 def test_backtest_next_open(self):
  rows=sample(); calls=[]
  def signal(history): calls.append(len(history));return {'action':'WATCH_LONG' if len(history)==61 else 'NO_SIGNAL'}
  with patch('research.evaluate',side_effect=signal): result=research.backtest(rows)
  self.assertEqual(calls[0],61);self.assertEqual(result['closed_trades'],1)
if __name__=='__main__':unittest.main()
