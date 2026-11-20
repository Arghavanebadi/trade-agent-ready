import tempfile, unittest
import sqlite3
from contextlib import closing
from pathlib import Path
from learner import observe
from headlines import feature

class ForwardTests(unittest.TestCase):
    def test_minimum_counts_directional_predictions_not_flat_outcomes(self):
        with tempfile.TemporaryDirectory() as location:
            path=Path(location)/'model.db'; now=1700000000
            votes=[{'name':'trend','vote':1}]
            first=observe(path,'venue','BTC',[],votes,0,now)
            target=first['target']
            with closing(sqlite3.connect(path)) as db, db:
                for i in range(1,60):
                    outcome=1 if i<=29 else 0
                    db.execute('INSERT INTO forecasts VALUES (?,?,?,?,?,?)',('venue','BTC',target-i*3600,'{"trend":1}',1,outcome))
            not_ready=observe(path,'venue','BTC',[],votes,0,now)
            self.assertEqual((not_ready['samples'],not_ready['directional_samples'],not_ready['direction']),(59,29,'WAIT'))
            with closing(sqlite3.connect(path)) as db, db:
                db.execute('UPDATE forecasts SET outcome=1 WHERE market=? AND symbol=? AND target=?',('venue','BTC',target-30*3600))
            ready=observe(path,'venue','BTC',[],votes,0,now)
            self.assertEqual((ready['directional_samples'],ready['direction']),(30,'LONG'))

    def test_pending_older_than_available_history_can_later_settle(self):
        with tempfile.TemporaryDirectory() as location:
            path=Path(location)/'model.db'; now=1700000000
            votes=[{'name':'trend','vote':1}]
            first=observe(path,'venue','BTC',[],votes,0,now)
            old_target=first['target']
            self.assertEqual((first['pending_count'],first['pending_outside_history']),(1,None))
            later=old_target+20*3600
            recent_bar={'time':old_target+10*3600,'open':10,'close':11}
            pending=observe(path,'venue','BTC',[recent_bar],votes,0,later)
            self.assertEqual((pending['pending_count'],pending['pending_outside_history']),(2,1))
            old_bar={'time':old_target,'open':10,'close':11}
            resolved=observe(path,'venue','BTC',[old_bar,recent_bar],votes,0,later)
            self.assertEqual((resolved['pending_count'],resolved['pending_outside_history'],resolved['samples']),(1,0,1))

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
