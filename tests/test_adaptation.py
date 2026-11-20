import tempfile, unittest
from pathlib import Path
from learner import observe

class AdaptationTests(unittest.TestCase):
    def test_reversal_shifts_weights_and_baseline_uses_frozen_votes(self):
        with tempfile.TemporaryDirectory() as folder:
            db=Path(folder)/'learn.db'
            roles=[dict(name='trend',vote=1),dict(name='reverse',vote=-1),dict(name='third',vote=1)]
            rows=[]
            for i in range(1,162):
                result=observe(db,'feed','BTC',rows,roles,0,i*3600)
                if i==81: early=result['weights']['trend']
                rows.append(dict(time=(i+1)*3600,open=10,close=11 if i<=80 else 9))
            self.assertGreater(early,.5)
            self.assertLess(result['weights']['trend'],.5)
            self.assertGreater(result['weights']['reverse'],.5)
            c=result['comparison']
            self.assertGreater(c['paired'],0)
            self.assertLessEqual(c['adaptive_correct'],c['paired'])
            again=observe(db,'feed','BTC',rows,roles,0,161*3600+30)
            self.assertEqual(result['comparison'],again['comparison'])
            other=observe(db,'feed','ETH',rows,roles,0,161*3600)
            self.assertEqual(other['agents'],[])
