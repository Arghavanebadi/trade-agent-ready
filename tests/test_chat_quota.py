import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from chat_quota import ChatQuota

class ChatQuotaTests(unittest.TestCase):
 def test_limit_survives_restart_and_resets_in_utc(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'usage.db'; quota=ChatQuota(path,2)
   self.assertTrue(quota.consume(1700000000)); self.assertTrue(quota.consume(1700000001))
   self.assertFalse(ChatQuota(path,2).consume(1700000002))
   self.assertTrue(quota.consume(1700086400))
 def test_concurrent_requests_cannot_exceed_limit(self):
  with tempfile.TemporaryDirectory() as temp:
   quota=ChatQuota(Path(temp)/'usage.db',3)
   with ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(lambda _:quota.consume(1700000000),range(12)))
   self.assertEqual(sum(results),3)
