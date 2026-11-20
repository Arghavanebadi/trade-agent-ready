"""Persistent installation-wide quota, counted on model requests in UTC."""
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

class ChatQuota:
 def __init__(self,path,limit=None):
  self.path=Path(path)
  try: self.limit=max(1,min(1000,int(limit if limit is not None else os.getenv('CHAT_DAILY_LIMIT','25'))))
  except ValueError: self.limit=25
 def consume(self,now=None):
  day=datetime.fromtimestamp(now,timezone.utc).date().isoformat() if now is not None else datetime.now(timezone.utc).date().isoformat()
  self.path.parent.mkdir(parents=True,exist_ok=True)
  with closing(sqlite3.connect(self.path,timeout=5)) as db:
   db.execute('CREATE TABLE IF NOT EXISTS chat_usage (day TEXT PRIMARY KEY, requests INTEGER NOT NULL)')
   db.execute('BEGIN IMMEDIATE')
   row=db.execute('SELECT requests FROM chat_usage WHERE day=?',(day,)).fetchone()
   count=row[0] if row else 0
   if count>=self.limit:
    db.rollback(); return False
   db.execute('INSERT INTO chat_usage(day,requests) VALUES (?,1) ON CONFLICT(day) DO UPDATE SET requests=requests+1',(day,))
   db.commit(); return True
