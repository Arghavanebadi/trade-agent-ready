"""Minimal public Bybit V5 adapter for USDT linear perpetual market data."""
import json, re, urllib.parse, urllib.request

class BybitPublic:
 has={'fetchFundingRate':True,'fetchOpenInterest':True}
 def __init__(self,symbols): self.symbols=symbols;self.tickers={}
 def api(self,path,params):
  params={'category':'linear',**params}
  url='https://api.bybit.com/v5/market/'+path+'?'+urllib.parse.urlencode(params)
  req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'FuturesResearch/1.0'})
  with urllib.request.urlopen(req,timeout=12) as response: data=json.load(response)
  if data.get('retCode')!=0: raise ValueError('Bybit API: '+str(data.get('retMsg','unknown'))[:120])
  return data['result']
 @staticmethod
 def native(symbol):
  match=re.fullmatch(r'([\w]{1,64})/USDT:USDT',symbol)
  if not match: raise ValueError('نماد قرارداد USDT نامعتبر است')
  return match.group(1)+'USDT'
 def load_markets(self):
  markets={}
  for symbol in self.symbols:
   try:
    items=self.api('instruments-info',{'symbol':self.native(symbol)}).get('list',[])
    if not items: continue
    obj=items[0]
    markets[symbol]={'swap':obj.get('contractType')=='LinearPerpetual','linear':True,'settle':obj.get('settleCoin'),'active':obj.get('status')=='Trading'}
   except ValueError: continue
  return markets
 def fetch_ohlcv(self,symbol,timeframe='1h',limit=120):
  if timeframe!='1h': raise ValueError('بازه پشتیبانی نمی‌شود')
  result=self.api('kline',{'symbol':self.native(symbol),'interval':'60','limit':limit})
  rows=result.get('list',[])
  return sorted([[int(x[0]),*[float(v) for v in x[1:6]]] for x in rows],key=lambda x:x[0])
 def ticker(self,symbol):
  if symbol not in self.tickers:
   rows=self.api('tickers',{'symbol':self.native(symbol)}).get('list',[])
   if not rows: raise ValueError('داده تکمیلی موجود نیست')
   self.tickers[symbol]=rows[0]
  return self.tickers[symbol]
 def fetch_funding_rate(self,symbol):
  value=self.ticker(symbol).get('fundingRate')
  return {'fundingRate':float(value) if value not in (None,'') else None}
 def fetch_open_interest(self,symbol):
  value=self.ticker(symbol).get('openInterest')
  return {'openInterestAmount':float(value) if value not in (None,'') else None}
 def catalog(self):
  markets={}; cursor=''; seen=set()
  while True:
   page=self.api('instruments-info',{'limit':1000,'cursor':cursor})
   for m in page['list']:
    base=m.get('baseCoin','')
    if base and m.get('symbol')==base+'USDT' and m.get('contractType')=='LinearPerpetual' and m.get('settleCoin')=='USDT' and m.get('status')=='Trading':
     markets[base+'/USDT:USDT']={'swap':True,'linear':True,'settle':'USDT','active':True}
   cursor=page.get('nextPageCursor')
   if not cursor: return markets
   if cursor in seen: raise ValueError('catalog cursor repeated')
   seen.add(cursor)
 def flow(self,symbol,now):
  import math
  buy=sell=count=0;seen=set()
  for r in self.api('recent-trade',{'symbol':self.native(symbol),'limit':500})['list']:
   try:
    uid=r['execId'];p=float(r['price']);q=float(r['size']);v=p*q
    if not uid or uid in seen or not math.isfinite(v) or min(p,q)<=0 or v<100000 or not 0<=now-float(r['time'])/1000<=300 or r['symbol']!=self.native(symbol) or r['side'] not in ('Buy','Sell'):continue
    seen.add(uid);count+=1
    if r['side']=='Buy':buy+=v
    else:sell+=v
   except (KeyError,ValueError,TypeError):continue
  vote=0 if count<3 else 1 if buy>2*sell else -1 if sell>2*buy else 0
  return dict(count=count,buy=buy,sell=sell,vote=vote)
