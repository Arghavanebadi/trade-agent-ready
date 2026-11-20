import unittest
from unittest.mock import patch
import diagnostics

def bars(count):
 return [{'time':i*3600,'open':100+i,'high':101+i,'low':99+i,'close':100+i,'volume':1} for i in range(count)]
class DiagnosticsTests(unittest.TestCase):
 def test_no_future_information_and_neutral_ignored(self):
  calls=[]
  def fake(rows):
   calls.append(len(rows));return {'agents':[{'name':'up','vote':1},{'name':'down','vote':-1},{'name':'neutral','vote':0}]}
  with patch('diagnostics.research.evaluate',side_effect=fake): result=diagnostics.evaluate_votes(bars(63))
  self.assertEqual(calls,[60,61,62]); self.assertEqual(result['windows'],3)
  byname={x['name']:x for x in result['agents']}
  self.assertEqual(byname['up']['accuracy_pct'],100);self.assertEqual(byname['down']['accuracy_pct'],0)
  self.assertTrue(byname['up']['insufficient']);self.assertNotIn('neutral',byname)
  self.assertFalse(result['training']);self.assertFalse(result['strategy_modified'])
 def test_invalid_data_rejected(self):
  rows=bars(61);rows[-1]['time']=0
  with self.assertRaises(ValueError): diagnostics.evaluate_votes(rows)
if __name__=='__main__':unittest.main()
