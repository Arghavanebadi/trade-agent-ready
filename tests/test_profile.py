import unittest
from risk_profile import assess
from risk import Limits, Rejected, plan

class ProfileTests(unittest.TestCase):
 def test_conservative_override(self):
  a={'horizon':'over_three','experience':'experienced','loss':'twenty','capacity':'essential','emergency':'yes'}
  self.assertEqual(assess(a)['level'],'low')
  a['capacity']='surplus';self.assertEqual(assess(a)['level'],'high')
  a['emergency']='no';self.assertEqual(assess(a)['level'],'low')
 def test_invalid_and_extra_fields(self):
  with self.assertRaises(ValueError):assess({})
  with self.assertRaises(ValueError):assess({'horizon':'bad','experience':'none','loss':'five','capacity':'surplus','emergency':'yes'})
 def test_risk_limit_one_percent(self):
  s={'symbol':'BTC','direction':'LONG','created_at':10000,'last_candle':6400,'price':100,'stop':95,'target':110}
  kw={'now':10000,'equity':10000,'daily_pnl':0,'positions':0,'halted':False,'reference_price':100,'reference_time':10000}
  with self.assertRaises(Rejected):plan(s,**kw,limits=Limits(risk_fraction=.0101))
  self.assertLessEqual(plan(s,**kw,limits=Limits(risk_fraction=.01))['estimated_stop_loss'],100)
if __name__=='__main__':unittest.main()

