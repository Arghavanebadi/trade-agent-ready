"""Time-bounded public RSS headline features; no model or exchange credentials."""
from email.utils import parsedate_to_datetime
import re
import urllib.request
import xml.etree.ElementTree as ET

FEED = 'https://www.coindesk.com/arc/outboundfeeds/rss/'
ALIASES = {'BTC':('bitcoin','btc'),'ETH':('ether','ethereum','eth'),'SOL':('solana','sol')}
UP = {'rally','rallies','surges','gains','approval','inflows'}
DOWN = {'crash','falls','plunges','outflows','hack','lawsuit'}

def fetch():
    req=urllib.request.Request(FEED,headers={'User-Agent':'TradeAgentReady/1.0 (RSS reader)'})
    with urllib.request.urlopen(req,timeout=5) as response:
        raw=response.read(512001)
    if len(raw)>512000 or b'<!ENTITY' in raw.upper(): raise ValueError('unsupported feed')
    items=[]
    for item in ET.fromstring(raw).findall('./channel/item')[:100]:
        title=item.findtext('title') or ''
        try: stamp=parsedate_to_datetime(item.findtext('pubDate')).timestamp()
        except (ValueError,TypeError,AttributeError,OverflowError): continue
        if title: items.append((stamp,title[:400]))
    return items

def feature(items,symbol,now):
    asset=symbol.split('/')[0]
    aliases=set(ALIASES.get(asset,(asset.lower(),)))
    titles=[]; total=0
    for stamp,title in items:
        words=set(re.findall(r'[a-z]+',title.lower()))
        if not 0<=now-stamp<=86400 or not words&aliases or title in titles: continue
        titles.append(title)
        total+=len(words&UP)-len(words&DOWN)
    return {'source':'CoinDesk RSS','available':True,'headlines':titles[:5],'matched':len(titles),'vote':(total>0)-(total<0)}
