import tempfile, unittest
from pathlib import Path
from learner import observe
from headlines import feature

class ForwardTests(unittest.TestCase):
    def test_first_prediction_immutable_and_scored_only_after_close(self):
        with tempfile.TemporaryDirectory() as location:
            path=Path(location)/'model.db'
            def tick(now,v,rows):
                return observe(path,'venue','BTC',rows,[{'name':'trend','vote':v}],0,now)
            self.assertEqual(tick(10,1,[])['score'],1)
            self.assertEqual(tick(20,-1,[])['score'],1)
            bar={'time':3600,'open':10,'close':11}
            self.assertEqual(tick(7199,-1,[bar])['samples'],0)
            final=tick(7200,-1,[bar])
            self.assertEqual((final['samples'],final['correct'],final['direction']),(1,1,'WAIT'))
            self.assertGreater(final['weights']['trend'],.5)
            self.assertEqual(tick(7201,-1,[bar])['samples'],1)

    def test_news_dedup_and_scope(self):
        news=feature([(100,'Bitcoin gains'),(100,'Bitcoin gains'),(101,'Bitcoin hack'),(99,'Solana falls')],'BTC/USDT:USDT',100)
        self.assertEqual((news['matched'],news['vote']),(1,1))

    def test_ambiguous_symbol_does_not_match_common_words(self):
        news=feature([(100,'One analyst says the market gains')],'ONE/USDT:USDT',100)
        self.assertFalse(news['available']); self.assertEqual(news['vote'],0)
        self.assertEqual(news['headlines'],[])
