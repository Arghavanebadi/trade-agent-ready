import time, unittest
from risk import Limits, Rejected, plan

class RiskTests(unittest.TestCase):
 def setUp(self):
  self.now=1_800_000_000
  self.signal={'symbol':'BTC/USDT:USDT','direction':'LONG','created_at':self.now-10,'last_candle':self.now-3600,'price':100.,'stop':95.,'target':110.}
  self.kw={'now':self.now,'equity':10000.,'daily_pnl':0.,'positions':0,'halted':False,'reference_price':100.,'reference_time':self.now-5}
 def test_size_capped_and_no_execution(self):
  p=plan(self.signal,**self.kw);self.assertEqual(p['notional'],100);self.assertFalse(p['execution_enabled'])
 def test_halt_loss_positions_and_stale(self):
  for key,value in [('halted',True),('daily_pnl',-200),('positions',1),('reference_time',self.now-61),('reference_price',101)]:
   with self.subTest(key=key):
    with self.assertRaises(Rejected): plan(self.signal,**{**self.kw,key:value})
 def test_short_and_invalid_levels(self):
  signal={**self.signal,'direction':'SHORT','stop':105.,'target':90.};self.assertGreater(plan(signal,**self.kw)['quantity_unrounded'],0)
  with self.assertRaises(Rejected): plan({**signal,'stop':95},**self.kw)
 def test_nonfinite_and_future(self):
  for bad in (float('nan'),float('inf'),-1):
   with self.assertRaises(Rejected): plan(self.signal,**{**self.kw,'equity':bad})
  with self.assertRaises(Rejected): plan({**self.signal,'created_at':self.now+1},**self.kw)
 def test_invalid_limits(self):
  with self.assertRaises(Rejected): plan(self.signal,**self.kw,limits=Limits(risk_fraction=1))

if __name__=='__main__':unittest.main()
