"""Append-only local log of scan outcomes; no credentials are persisted."""
import json, sqlite3, time
from contextlib import closing
from pathlib import Path

class Audit:
 def __init__(self, path): self.path=Path(path)
 def history(self, symbol, now=None, days=7):
  if not self.path.exists() or not isinstance(symbol,str): return []
  from datetime import datetime, timezone
  now=time.time() if now is None else now
  selected=[]; seen=set()
  with closing(sqlite3.connect(self.path,timeout=5)) as db:
   exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='scans'").fetchone()
   if not exists: return []
   rows=db.execute('SELECT timestamp,payload FROM scans WHERE timestamp>=? AND timestamp<=? ORDER BY id DESC LIMIT 3000',(now-days*86400,now))
   for stamp,payload in rows:
    day=datetime.fromtimestamp(stamp,timezone.utc).date().isoformat()
    if day in seen: continue
    report=json.loads(payload)
    result=next((entry for entry in report.get('results',[]) if entry.get('symbol')==symbol),None)
    if result:
     selected.append({'recorded_at':stamp,**result}); seen.add(day)
  return selected
 def recent(self, limit=30):
  if not self.path.exists(): return []
  limit=max(1,min(int(limit),100))
  with closing(sqlite3.connect(self.path,timeout=5)) as db:
   exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='scans'").fetchone()
   if not exists: return []
   rows=db.execute('SELECT id,timestamp,payload FROM scans ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
  return [{'id':row[0],'timestamp':row[1],'report':json.loads(row[2])} for row in rows]
 def record(self, state):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  entries=[]
  for item in state.get('results',[]):
   entries.append({k:item.get(k) for k in ('symbol','direction','votes','price','stop','target','last_candle')})
   entries[-1]['agents']=[{k:a.get(k) for k in ('role','detail','status','vote')} for a in item.get('agents',[])]
  payload=json.dumps({'exchange':state.get('exchange'),'status':state.get('status'),'results':entries},ensure_ascii=False,allow_nan=False)
  with closing(sqlite3.connect(self.path,timeout=5)) as db, db:
   db.execute('CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, timestamp REAL NOT NULL, payload TEXT NOT NULL)')
   db.execute('INSERT INTO scans(timestamp,payload) VALUES (?,?)',(time.time(),payload))
