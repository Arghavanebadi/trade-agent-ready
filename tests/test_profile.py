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
 def test_additional_risk_flags_override_high_score(self):
  answers={'horizon':'over_three','experience':'experienced','loss':'twenty','capacity':'surplus','emergency':'yes','leverage_experience':'experienced','borrowed_funds':'no','loss_response':'plan'}
  self.assertEqual(assess(answers)['level'],'high')
  for key,value in [('leverage_experience','none'),('borrowed_funds','yes'),('loss_response','exit')]:
   changed={**answers,key:value}; result=assess(changed)
   self.assertEqual(result['level'],'low'); self.assertTrue(result['reasons'])
  with self.assertRaises(ValueError):assess({**answers,'borrowed_funds':'unknown'})
 def test_risk_limit_one_percent(self):
  s={'symbol':'BTC','direction':'LONG','created_at':10000,'last_candle':6400,'price':100,'stop':95,'target':110}
  kw={'now':10000,'equity':10000,'daily_pnl':0,'positions':0,'halted':False,'reference_price':100,'reference_time':10000}
  with self.assertRaises(Rejected):plan(s,**kw,limits=Limits(risk_fraction=.0101))
  self.assertLessEqual(plan(s,**kw,limits=Limits(risk_fraction=.01))['estimated_stop_loss'],100)
if __name__=='__main__':unittest.main()

