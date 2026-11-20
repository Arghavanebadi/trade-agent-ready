import json, sqlite3, tempfile, unittest
from pathlib import Path
from contextlib import closing
from audit import Audit
class AuditTests(unittest.TestCase):
 def test_history_filters_market_and_current_candle(self):
  with tempfile.TemporaryDirectory() as temp:
   audit=Audit(Path(temp)/'audit.db')
   from unittest.mock import patch
   for timestamp,market,candle in [(1700000000,'a',3600),(1700000010,'a',7200),(1700000020,'b',3600)]:
    with patch('audit.time.time',return_value=timestamp):
     audit.record({'exchange':market,'results':[{'symbol':'BTC','last_candle':candle}]})
   history=audit.history('BTC',now=1700000030,market='a',before_candle=7200)
   self.assertEqual(len(history),1)
   self.assertEqual(history[0]['last_candle'],3600)
 def test_history_is_symbol_scoped_and_latest_per_day(self):
  with tempfile.TemporaryDirectory() as temp:
   audit=Audit(Path(temp)/'audit.db')
   from unittest.mock import patch
   for stamp,symbol,price in [(1700000000,'BTC',1),(1700000010,'BTC',2),(1700000020,'ETH',9),(1700086400,'BTC',3)]:
    with patch('audit.time.time',return_value=stamp):
     audit.record({'results':[{'symbol':symbol,'price':price}]})
   history=audit.history('BTC',now=1700086401)
   self.assertEqual([entry['price'] for entry in history],[3,2])
 def test_audit_persists_only_allowlisted_fields(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'audit.db'; a=Audit(path);a.record({'exchange':'test','status':'running','results':[{'symbol':'BTC','direction':'LONG','api_key':'secret'}]})
   with closing(sqlite3.connect(path)) as db: payload=json.loads(db.execute('select payload from scans').fetchone()[0])
   self.assertEqual(payload['results'][0]['symbol'],'BTC');self.assertNotIn('secret',json.dumps(payload))
if __name__=='__main__':unittest.main()
