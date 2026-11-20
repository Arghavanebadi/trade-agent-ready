import json, sqlite3, tempfile, unittest
from pathlib import Path
from contextlib import closing
from audit import Audit
class AuditTests(unittest.TestCase):
 def test_audit_persists_only_allowlisted_fields(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'audit.db'; a=Audit(path);a.record({'exchange':'test','status':'running','results':[{'symbol':'BTC','direction':'LONG','api_key':'secret'}]})
   with closing(sqlite3.connect(path)) as db: payload=json.loads(db.execute('select payload from scans').fetchone()[0])
   self.assertEqual(payload['results'][0]['symbol'],'BTC');self.assertNotIn('secret',json.dumps(payload))
if __name__=='__main__':unittest.main()
