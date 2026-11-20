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
        # Model metadata lives separately so earlier forecasts remain readable.
        db.execute('CREATE TABLE IF NOT EXISTS learning_versions (market TEXT,symbol TEXT,target INTEGER, PRIMARY KEY(market,symbol,target))')
        history = db.execute("""
            SELECT f.target,f.features,f.outcome,f.score,v.target IS NOT NULL
            FROM forecasts f LEFT JOIN learning_versions v USING(market,symbol,target)
            WHERE f.market=? AND f.symbol=? AND f.outcome IS NOT NULL AND f.target<?
            ORDER BY f.target DESC LIMIT 240""", (*key,target)).fetchall()
        settled = len(history)
        stats = {}
        hits = guesses = paired = adapted_hits = baseline_hits = 0
        for stamp, fv, outcome, oldscore, current_version in history:
            recorded = json.loads(fv)
            if not outcome:
                continue
            baseline = sum(recorded.values()) / (len(recorded) or 1)
            if abs(oldscore) >= .25:
                guesses += 1
                hits += oldscore*outcome > 0
            if current_version and abs(oldscore)>=.25 and abs(baseline)>=.25:
                paired += 1
                adapted_hits += oldscore*outcome>0
                baseline_hits += baseline*outcome>0
            # Old observations lose half their influence every 48 market hours.
            decay = .5 ** ((target-stamp)/(48*3600))
            for name,v in recorded.items():
                row=stats.setdefault(name,dict(samples=0,correct=0,mass=0.,wins=0.,last_target=stamp))
                correct=int(v==outcome)
                row['samples']+=1; row['correct']+=correct
                row['mass']+=decay; row['wins']+=decay*correct
        w={name:(row['wins']+5)/(row['mass']+10) for name,row in stats.items()}
        score=sum(v*w.get(k,.5) for k,v in features.items())/(sum(w.get(k,.5) for k in features) or 1)
        inserted=db.execute('INSERT OR IGNORE INTO forecasts VALUES (?,?,?,?,?,NULL)',(*key,target,json.dumps(features),score)).rowcount
        if inserted:
            db.execute('INSERT INTO learning_versions VALUES (?,?,?)',(*key,target))
        score, = db.execute('SELECT score FROM forecasts WHERE market=? AND symbol=? AND target=?',(*key,target)).fetchone()
        earliest = min(bars) if bars else None
        pending_count, outside_history = db.execute('''SELECT COUNT(*), COALESCE(SUM(CASE WHEN target < ? AND target + 3600 <= ? THEN 1 ELSE 0 END), 0)
            FROM forecasts WHERE market=? AND symbol=? AND outcome IS NULL''',(earliest,observed_at,*key)).fetchone()
        if earliest is None: outside_history = None
        agents=[dict(name=name,samples=r['samples'],correct=r['correct'],weight=w[name],last_target=r['last_target']) for name,r in stats.items()]
        return dict(target=target,score=score,samples=settled,directional_samples=guesses,correct=hits,weights=w,
                    agents=agents, last_settled=history[0][0]+3600 if history else None,
                    pending_count=pending_count, pending_outside_history=outside_history,
                    comparison=dict(paired=paired,adaptive_correct=adapted_hits,baseline_correct=baseline_hits),
                    direction='WAIT' if guesses<30 or abs(score)<.25 else 'LONG' if score>0 else 'SHORT')
