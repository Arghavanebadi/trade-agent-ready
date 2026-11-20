import unittest

from app import public_error


class PublicErrorTests(unittest.TestCase):
 def test_errors_are_actionable_without_exposing_raw_details(self):
  self.assertIn('403',public_error('HTTP Error 403: Forbidden'))
  self.assertIn('محدودیت',public_error('HTTP Error 429: Too Many Requests'))
  self.assertIn('خبر',public_error('دریافت خبر ناموفق بود'))
  self.assertNotIn('secret-host',public_error('secret-host connection failed'))


if __name__=='__main__': unittest.main()
