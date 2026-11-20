"""Persistent, forward-only ensemble. Predictions are research observations."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

def observe(path, market, symbol, rows, votes, news_vote, observed_at):
    # Target starts at the first whole hour AFTER observation. News read during
    # the current hour can never be scored against a bar already in progress.
    target = (int(observed_at)//3600 + 1)*3600
    features = {a['name']: a['vote'] for a in votes if a['vote'] in (-1, 1)}
    if news_vote in (-1, 1):
        features['News headlines'] = news_vote
    bars = {int(b['time']): b for b in rows if b['time']+3600 <= observed_at}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS forecasts (market TEXT,symbol TEXT,target INTEGER,features TEXT,score REAL,outcome INTEGER,PRIMARY KEY(market,symbol,target))')
        key = (market, symbol)
        db.execute('BEGIN IMMEDIATE')
        for t, in db.execute('SELECT target FROM forecasts WHERE market=? AND symbol=? AND outcome IS NULL',key).fetchall():
            if t in bars:
                delta = bars[t]['close'] - bars[t]['open']
                db.execute('UPDATE forecasts SET outcome=? WHERE market=? AND symbol=? AND target=?',((delta>0)-(delta<0),*key,t))
        weights = {}
        settled = hits = guesses = 0
        for fv, outcome, oldscore in db.execute('SELECT features,outcome,score FROM forecasts WHERE market=? AND symbol=? AND outcome IS NOT NULL AND target<? ORDER BY target DESC LIMIT 240',(*key,target)):
            settled += 1
            if outcome and abs(oldscore)>=0.25:
                guesses += 1
                hits += oldscore*outcome>0
            for name,v in json.loads(fv).items():
                if outcome:
                    wins,n = weights.get(name,(0,0))
                    weights[name]=(wins+int(v==outcome),n+1)
        w = {k:(v+5)/(n+10) for k,(v,n) in weights.items()}
        score = sum(v*w.get(k,.5) for k,v in features.items()) / (sum(w.get(k,.5) for k in features) or 1)
        db.execute('INSERT OR IGNORE INTO forecasts VALUES (?,?,?,?,?,NULL)',(*key,target,json.dumps(features),score))
        score, = db.execute('SELECT score FROM forecasts WHERE market=? AND symbol=? AND target=?',(*key,target)).fetchone()
        return dict(target=target,score=score,samples=settled, directional_samples=guesses, correct=hits, weights=w,
                    direction='WAIT' if settled<30 or abs(score)<.25 else 'LONG' if score>0 else 'SHORT')
