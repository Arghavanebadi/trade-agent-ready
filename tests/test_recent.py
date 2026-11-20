import tempfile, unittest
from pathlib import Path
from audit import Audit
class RecentTests(unittest.TestCase):
 def test_empty_and_latest_first(self):
  with tempfile.TemporaryDirectory() as d:
   audit=Audit(Path(d)/'audit.db');self.assertEqual(audit.recent(),[])
   audit.record({'exchange':'first','status':'error','results':[]});audit.record({'exchange':'second','status':'running','results':[]})
   self.assertEqual([x['report']['exchange'] for x in audit.recent(1)],['second'])
   self.assertEqual(len(audit.recent()),2)
if __name__=='__main__':unittest.main()
