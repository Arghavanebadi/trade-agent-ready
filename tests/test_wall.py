import unittest
from unittest.mock import patch
from bybit_public import BybitPublic

class WallTests(unittest.TestCase):
 def test_catalog_reads_next_page_and_filters_expired_contracts(self):
  def market(base,active=True):
   return dict(baseCoin=base,symbol=base+'USDT',settleCoin='USDT',contractType='LinearPerpetual',status='Trading' if active else 'Closed')
  adapter=BybitPublic([])
  with patch.object(adapter,'api',side_effect=[{'list':[market('BTC')],'nextPageCursor':'p2'},{'list':[market('X'),market('BAD',False)]}]) as mock:
   self.assertEqual(set(adapter.catalog()),{'BTC/USDT:USDT','X/USDT:USDT'})
   self.assertEqual(mock.call_args.args[1]['cursor'],'p2')
 def test_flow_excludes_old_small_and_duplicate_prints(self):
  adapter=BybitPublic([])
  def trade(i,t=900000,size='2'):
   return dict(time=t,price='60000',size=size,execId=i,symbol='BTCUSDT',side='Buy')
  records=[trade('A'),trade('A'),trade('B'),trade('C'),trade('D',0),trade('E',size='1')]
  with patch.object(adapter,'api',return_value={'list':records}):
   result=adapter.flow('BTC/USDT:USDT',1000)
   self.assertEqual((result['count'],result['buy'],result['vote']),(3,360000,1))
