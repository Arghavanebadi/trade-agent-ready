import json, os
import risk_profile, analyst, news_digest
from chat_quota import ChatQuota
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from scanner import FuturesScanner
from audit import Audit

ROOT=Path(__file__).resolve().parent
scanner=FuturesScanner()
news_monitor=news_digest.NewsMonitor()
chat_quota=ChatQuota(ROOT/'data'/'chat_usage.sqlite3')
def public_error(message):
 text=str(message).lower()
 if '403' in text or 'forbidden' in text: return 'منبع بازار دسترسی را رد کرد (HTTP 403). اتصال و دسترسی شبکه را بررسی کنید.'
 if '429' in text or 'rate limit' in text: return 'محدودیت تعداد درخواست منبع بازار فعال است؛ کمی بعد دوباره تلاش می‌شود.'
 if 'timed out' in text or 'timeout' in text: return 'پاسخ منبع بازار به‌موقع نرسید؛ اتصال را بررسی کنید.'
 if 'خبر' in text: return 'دریافت یا پردازش خبر ناموفق بود؛ تحلیل قیمت در صورت دسترسی ادامه دارد.'
 if 'تاریخی' in text or 'تطبیقی' in text: return 'ارزیابی تکمیلی در دسترس نیست؛ تحلیل قیمت در صورت دسترسی ادامه دارد.'
 if 'ثبت' in text: return 'ثبت محلی گزارش یا فهرست ناموفق بود؛ دسترسی پوشه داده را بررسی کنید.'
 if 'اسکن پایان' in text: return 'این نوبت بدون دریافت داده معتبر پایان یافت.'
 return 'داده معتبر دریافت نشد؛ اتصال، دسترسی منبع و وضعیت داده را بررسی کنید.'
class Handler(BaseHTTPRequestHandler):
 def do_POST(self):
  try:
   if self.path not in ('/api/analyze','/api/risk-profile','/api/chat'): self.send_error(404); return
   host=self.headers.get('Host',''); port=self.server.server_port
   allowed=(f'127.0.0.1:{port}',f'localhost:{port}')
   if host not in allowed or (self.headers.get('Origin') and self.headers['Origin'] not in tuple('http://'+x for x in allowed)): raise ValueError('درخواست نامعتبر است')
   if self.headers.get_content_type()!='application/json': raise ValueError('نوع درخواست نامعتبر است')
   length=int(self.headers.get('Content-Length','0'))
   if length<1 or length>(65536 if self.path=='/api/chat' else 1024): raise ValueError('اندازه درخواست نامعتبر است')
   data=json.loads(self.rfile.read(length))
   if self.path=='/api/analyze': scanner.request_analysis(data.get('symbol')); result={'ok':True}; status=202
   elif self.path=='/api/chat':
    state=scanner.get(); symbol=data.get('symbol')
    current=next((row for row in state['results'] if row['symbol']==symbol),None)
    history=Audit(ROOT/'data'/'audit.sqlite3').history(symbol,market=state.get('exchange'),before_candle=current.get('last_candle') if current else None) if symbol in state['symbols'] else []
    result=analyst.reply(state,data,historical=history,quota=chat_quota); status=200
   else: result=risk_profile.assess(data); status=200
   body=json.dumps(result,ensure_ascii=False).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
  except (ValueError,TypeError,AttributeError): self.send_error(400,'Invalid request')
  except (OSError,__import__('sqlite3').Error): self.send_error(503,'Storage unavailable')
 def do_GET(self):
  route=urlparse(self.path).path
  if route in ('/api/scan','/api/reports','/api/news'):
   try:
    data=scanner.get() if route=='/api/scan' else news_monitor.get() if route=='/api/news' else {'reports':Audit(ROOT/'data'/'audit.sqlite3').recent()}
    if route=='/api/scan':
     venue=data.pop('exchange','')
     data['ticker_supported']=venue=='bybit'
     link=os.getenv('CREATOR_LINKEDIN_URL','')
     data['linkedin']=link if __import__('re').fullmatch(r'https://(?:www\.)?linkedin\.com/in/[\w%-]+/?',link) else None
     for event in data.get('activity',[]):
      if event.get('level')=='error': event['message']=public_error(event['message'])
      elif venue: event['message']=event['message'].replace(venue,'منبع بازار')
     for err in data.get('errors',[]): err['error']=public_error(err['error'])
     for result in data.get('results',[]):
      news=result.get('news',{})
      if venue: news['headlines']=[t for t in news.get('headlines',[]) if venue.lower() not in t.lower()]
    elif route=='/api/reports':
     for entry in data['reports']: entry['report'].pop('exchange',None)
    body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode('utf-8'); mime='application/json; charset=utf-8'
   except (OSError, ValueError, __import__('sqlite3').Error): self.send_error(503,'Reports unavailable'); return
  else:
   files={'/':'index.html','/style.css':'style.css','/app.js':'app.js'}
   if route not in files: self.send_error(404); return
   file=ROOT/'static'/files[route]; body=file.read_bytes(); mime={'html':'text/html; charset=utf-8','css':'text/css; charset=utf-8','js':'text/javascript; charset=utf-8'}[file.suffix[1:]]
  self.send_response(200); self.send_header('Content-Type',mime); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(body)

if __name__=='__main__':
 scanner.start(); news_monitor.start(); port=int(os.getenv('PORT','8765')); print(f'Futures intelligence: http://127.0.0.1:{port}',flush=True)
 try: ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
 finally: scanner.stop(); news_monitor.stop()

