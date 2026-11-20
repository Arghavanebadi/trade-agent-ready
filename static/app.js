const $=id=>document.getElementById(id);let current=null;
function money(n){const value=Number(n);return n==null||!Number.isFinite(value)?'—':value.toLocaleString('en-US',{maximumSignificantDigits:10})}
let toastTimer;
function message(t){$('toast').textContent=t;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>{$('toast').classList.remove('show');$('toast').textContent=''},4000)}
function item(tag,text,cls){const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e}
const agentProfiles={
 'Trend architect':['📈','متخصص روند و میانگین‌های متحرک'],
 'Momentum analyst':['🎯','متخصص مومنتوم و قدرت حرکت'],
 'Volatility guard':['🌊','متخصص سنجش نوسان'],
 'Breakout watcher':['🚀','متخصص شکست محدوده'],
 'Mean reversion':['🧲','متخصص بازگشت به میانگین'],
 'Volume analyst':['📊','متخصص حجم معاملات'],
 'Price action':['⚡','متخصص بازده کوتاه‌مدت'],
 'Market regime':['🧭','متخصص وضعیت روند بازار'],
 'Risk manager':['🛡️','متخصص کنترل ریسک'],
 'Data quality':['🔎','متخصص اعتبارسنجی داده'],
 'Stochastic analyst':['🎚️','متخصص نوسان‌سنج استوکاستیک'],
 'VWAP analyst':['⚖️','متخصص میانگین وزنی حجم'],
 'Range analyst':['📐','متخصص دامنه قیمت'],
 'Candle analyst':['🕯️','متخصص ساختار کندل'],
 'Acceleration analyst':['🏎️','متخصص شتاب بازده']
};
const skipLink=item('a','رفتن به محتوای اصلی','skip-link');skipLink.href='#overview';document.body.prepend(skipLink);
const qualityDetails=item('div','','quality-details');qualityDetails.id='quality-details';$('quality').after(qualityDetails);
const candidates=item('section','','candidates');candidates.setAttribute('aria-label','فرصت‌های بررسی‌شده');$('results').before(candidates);
const chartPanel=item('section','','panel chart-panel');
const chartTitle=item('h3','نمودار قیمت');const chartNote=item('p','منتظر دریافت داده معتبر','tiny');const chartArea=item('div','','chart-area');
chartPanel.append(chartTitle,chartNote,chartArea);document.querySelector('.desk-hero').after(chartPanel);
const workflow=item('section','','panel workflow');workflow.setAttribute('aria-label','مسیر تحلیل');document.querySelector('.choose-panel').after(workflow);
const decisionPanel=item('section','','panel decision-panel');decisionPanel.id='decision-report';decisionPanel.setAttribute('aria-label','جمع‌بندی تحلیل');$('agents').after(decisionPanel);
document.querySelector('.choose-panel').after(document.querySelector('.notice'));
const marketDetails=item('details','','panel compact-details');marketDetails.append(item('summary','جزئیات بازار'));const overview=$('overview');for(const node of [overview.querySelector('.desk-hero'),overview.querySelector('.sectionhead'),overview.querySelector('.metrics'),overview.querySelector('.grid')])marketDetails.append(node);overview.append(marketDetails);
const extraDetails=item('details','','panel compact-details');extraDetails.id='more-tools';extraDetails.append(item('summary','ابزارها، تاریخچه و تنظیمات'));const operations=$('operations'),learningPanel=operations.nextElementSibling;operations.before(extraDetails);for(const node of [operations,learningPanel,$('diagnostics'),$('reports'),$('preferences')])extraDetails.append(node);
document.querySelectorAll('aside nav a').forEach(link=>link.addEventListener('click',()=>{if(extraDetails.contains(document.querySelector(link.hash)))extraDetails.open=true}));
function renderWorkflow(data,result){
 const symbol=$('contract').value,ready=Boolean(result&&usable(result)),scanning=['starting','scanning'].includes(data.status),focused=data.focus===symbol||data.progress?.symbol===symbol;
 const failed=!ready&&(data.status==='error'||data.status==='stale'||(data.errors||[]).some(error=>error.symbol===symbol||error.symbol==='*'));
 const active=!ready&&scanning&&focused;
 const progress=data.progress||{},stage=active&&progress.symbol===symbol?progress.stage:'queued',completed=ready?4:active?({queued:0,catalog:0,fetching:1,analyzing:2,enriching:3,complete:3}[stage]||0):0;
 const heading=item('div','','workflow-heading');const title=item('div','');title.append(item('span','ANALYSIS JOURNEY','eyebrow'),item('h3','مسیر بررسی '+(symbol||'بازار')));heading.append(title,item('span',ready?'گزارش آماده است':failed?'داده در دسترس نیست':active?'در حال دریافت و بررسی':'آماده شروع','workflow-status'));
 const meter=item('div','','journey-meter');meter.setAttribute('role','progressbar');meter.setAttribute('aria-label','مراحل تکمیل‌شده گزارش');meter.setAttribute('aria-valuemin','0');meter.setAttribute('aria-valuemax','4');meter.setAttribute('aria-valuenow',String(completed));const fill=item('span','','journey-fill');fill.style.width=(completed*25)+'%';meter.append(fill);
 const steps=item('div','','flow-steps');
 const definitions=[['درخواست',ready||active?'ثبت شد':'در انتظار',ready||active?'done':'waiting'],['داده بازار',ready||completed>=2?'دریافت شد':failed?'ناموفق':active?'در حال دریافت':'در انتظار',ready||completed>=2?'done':failed?'failed':active?'active':'waiting'],['تحلیل نقش‌ها',ready||completed>=3?'محاسبه شد':completed===2?'در حال محاسبه':'در انتظار',ready||completed>=3?'done':completed===2?'active':'waiting'],['گزارش نهایی',ready?'آماده مشاهده':completed===3?'در حال تکمیل':'در انتظار',ready?'done':completed===3?'active':'waiting']];
 definitions.forEach(([label,detail,state],index)=>{const step=item('div','','flow-step');step.dataset.state=state;const number=item('span',state==='done'?'✓':String(index+1),'flow-number');const copy=item('div','');copy.append(item('strong',label),item('small',detail));step.append(number,copy);steps.append(step)});
 const failure=(data.errors||[]).find(error=>error.symbol===symbol||error.symbol==='*');
 workflow.replaceChildren(heading,meter,steps,item('p',failed?(failure?.error||'داده تازه در دسترس نیست؛ اتصال را بررسی کنید.'):completed.toLocaleString('fa-IR')+' از ۴ مرحله تکمیل شد.','workflow-note'));
}
const profileKey='ebadi-risk-profile-v1';let personalProfile=null;
try{const stored=JSON.parse(localStorage.getItem(profileKey)||'null');if(stored&&['low','moderate','high'].includes(stored.level)&&typeof stored.name==='string')personalProfile=stored}catch(error){personalProfile=null}
function profileAdvice(result){
 if(!personalProfile)return 'پروفایل ریسک تکمیل نشده است.';
 const label={low:'کم',moderate:'متوسط',high:'بالا'}[personalProfile.level];
 if(!result||!usable(result))return 'پروفایل ریسک '+label+' · داده تازه لازم است.';
 if(result.direction==='WAIT')return 'پروفایل ریسک '+label+' · بدون سیگنال جهت‌دار.';
 if(personalProfile.level==='low')return 'ریسک کم · احتیاط؛ سیگنال صرفاً برای بررسی است.';
 if(personalProfile.level==='moderate'&&(result.direction==='LONG'?result.negative:result.positive)>0)return 'ریسک متوسط · رأی مخالف وجود دارد؛ بررسی بیشتر لازم است.';
 return 'پروفایل ریسک '+label+' · نتیجه صرفاً برای بررسی است.';
}
function renderDecision(result){
 const title=item('div','','decision-heading');const heading=item('div','');heading.append(item('span','ANALYSIS SUMMARY','eyebrow'),item('h2','جمع‌بندی و گزارش'));title.append(heading);
 if(!result||!usable(result)){decisionPanel.replaceChildren(title,item('p','در انتظار گزارش معتبر.','decision-empty'),item('p',profileAdvice(null),'profile-advice'));return}
 const labels={LONG:'تمایل صعودی',SHORT:'تمایل نزولی',WAIT:'بدون سیگنال'};const signal=item('span',labels[result.direction]||'بدون سیگنال','decision-signal');signal.dataset.direction=result.direction;title.append(signal);
 const meta=item('p',result.symbol+' · آخرین بررسی '+new Date(result.checked_at*1000).toLocaleString('fa-IR')+' · قیمت کندل بسته '+money(result.price)+' USDT','decision-meta');
 const agents=Array.isArray(result.agents)?result.agents:[],positive=agents.filter(agent=>agent.vote>0),negative=agents.filter(agent=>agent.vote<0),neutral=agents.length-positive.length-negative.length;
 const votes=item('div','','vote-summary');votes.append(item('h3','توزیع رأی نقش‌ها'));
 const bar=item('div','','vote-bar');bar.setAttribute('role','img');bar.setAttribute('aria-label',positive.length+' رأی مثبت، '+negative.length+' رأی منفی و '+neutral+' خنثی یا بدون رأی');
 for(const [count,kind] of [[positive.length,'positive'],[neutral,'neutral'],[negative.length,'negative']]){const part=item('span','','vote-'+kind);part.style.width=(agents.length?count/agents.length*100:0)+'%';bar.append(part)}
 const legend=item('div','','vote-legend');for(const [label,count,kind] of [['مثبت',positive.length,'positive'],['خنثی یا بدون رأی',neutral,'neutral'],['منفی',negative.length,'negative']])legend.append(item('span',label+' '+count.toLocaleString('fa-IR'),'legend-'+kind));votes.append(bar,legend,item('p','رأی جهت‌دار، احتمال موفقیت نیست.','tiny'));
 const levels=item('div','','decision-levels');for(const [label,value] of [['قیمت مرجع',result.price],['حد مرجع',result.stop],['هدف مرجع',result.target]]){const box=item('div','','decision-level');box.append(item('small',label),item('strong',money(value)));levels.append(box)}
 const evidence=item('div','','decision-evidence');for(const [label,list] of [['شواهد مثبت',positive],['شواهد منفی',negative]]){const box=item('div','','evidence-box');box.append(item('h4',label));if(!list.length)box.append(item('p','رأیی ثبت نشده است.'));for(const agent of list.slice(0,3))box.append(item('p',agent.role+' · '+agent.detail));evidence.append(box)}
 decisionPanel.replaceChildren(title,meta,item('p',profileAdvice(result),'profile-advice'),levels,votes,evidence,item('p','گزارش پژوهشی است؛ سطوح سفارش نیستند و سود را تضمین نمی‌کنند.','decision-footnote'));
}
function renderChart(result){
 chartArea.replaceChildren();
 if(!result||!usable(result)||!Array.isArray(result.candles)||result.candles.length<2){chartNote.textContent='در انتظار داده نمودار.';return}
 const rows=result.candles,high=Math.max(...rows.map(row=>row.high)),low=Math.min(...rows.map(row=>row.low)),span=high-low||high*.001;
 if(!Number.isFinite(span)||span<=0){chartNote.textContent='نمودار برای این داده در دسترس نیست.';return}
 chartNote.textContent=result.symbol+' · '+rows.length.toLocaleString('fa-IR')+' کندل بسته‌شده یک‌ساعته · آخرین بسته‌شدن '+new Date((result.last_candle+3600)*1000).toLocaleString('fa-IR');
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 800 260');svg.setAttribute('role','img');svg.setAttribute('aria-label','نمودار کندل‌های بسته‌شده '+result.symbol+'؛ بیشینه '+money(high)+'، کمینه '+money(low));
 const add=(name,attrs)=>{const node=document.createElementNS(ns,name);for(const [key,value] of Object.entries(attrs))node.setAttribute(key,String(value));svg.append(node);return node};
 const y=value=>20+(high-value)/span*200;
 for(let step=0;step<5;step++){const height=20+step*50;add('line',{x1:55,x2:790,y1:height,y2:height,class:'chart-grid'});const label=add('text',{x:49,y:height+4,'text-anchor':'end',class:'chart-label'});label.textContent=money(high-span*step/4)}
 const width=735/rows.length;
 rows.forEach((row,index)=>{const x=55+width*(index+.5),up=row.close>=row.open,top=y(Math.max(row.open,row.close)),bottom=y(Math.min(row.open,row.close)),color=up?'chart-up':'chart-down';add('line',{x1:x,x2:x,y1:y(row.high),y2:y(row.low),class:color});const body=add('rect',{x:x-Math.max(1,width*.3),y:top,width:Math.max(2,width*.6),height:Math.max(1,bottom-top),class:color});const title=document.createElementNS(ns,'title');title.textContent=new Date((row.time+3600)*1000).toLocaleString('fa-IR')+' · باز '+money(row.open)+' · بالا '+money(row.high)+' · پایین '+money(row.low)+' · بسته '+money(row.close);body.append(title)});
 chartArea.append(svg);
}
for(const [id,label] of [['download','دانلود گزارش HTML'],['refresh','به‌روزرسانی'],['reports-refresh','به‌روزرسانی تاریخچه']])$(id).setAttribute('aria-label',label);
function renderQuality(s){
 qualityDetails.replaceChildren();
 const next=current?.next_scan?new Date(current.next_scan*1000).toLocaleTimeString('fa-IR'):'در حال بررسی یا نامشخص';
 qualityDetails.append(item('p','بررسی بعدی: '+next),item('p','فاصله پایه بررسی: '+(current?.scan_interval_seconds||300).toLocaleString('fa-IR')+' ثانیه'));
 if(!s||!usable(s)){qualityDetails.append(item('p','گزارش تازه در دسترس نیست.'));return}
 const checked=new Date(s.checked_at*1000).toLocaleString('fa-IR');
 const close=new Date((s.last_candle+3600)*1000).toLocaleString('fa-IR');
 for(const text of ['زمان دریافت گزارش: '+checked,'زمان بسته‌شدن کندل: '+close,'سن گزارش: '+Math.floor((Date.now()/1000-s.checked_at)/60).toLocaleString('fa-IR')+' دقیقه','Funding: '+(s.funding_rate==null?'ناموجود':money(s.funding_rate)),'Open interest: '+(s.open_interest==null?'ناموجود':money(s.open_interest)),'جریان معاملات بزرگ: '+(s.flow?'دریافت شد':'ناموجود'),'خبر: '+(s.news?.available?'دریافت شد':'ناموجود')])qualityDetails.append(item('p',text));
}
function render(d){current=d;const dropdown=$('contract');fillMarkets(dropdown,d.symbols||[]);const selected=d.results.find(x=>x.symbol===dropdown.value&&usable(x));const status={starting:'در حال شروع',scanning:'در حال بررسی',running:'پایش فعال',error:'خطا در داده',stale:'داده قدیمی'};$('system-status').textContent=status[d.status]||d.status;$('exchange').textContent='کندل‌های یک‌ساعته';$('symbol').textContent=selected?selected.symbol:dropdown.value;$('direction').textContent=selected?(selected.direction==='WAIT'?'بدون سیگنال':selected.direction):'بدون سیگنال';$('price').textContent=selected?money(selected.price):'—';$('levels').textContent=selected?money(selected.stop)+' / '+money(selected.target):'—';$('votes').textContent=selected?selected.positive+' مثبت / '+selected.negative+' منفی':'—';$('scan-time').textContent=d.last_scan?'آخرین بررسی: '+new Date(d.last_scan*1000).toLocaleString('fa-IR'):'هنوز بررسی موفقی انجام نشده است.';$('results').replaceChildren();if(!d.results.length)$('results').append(item('p','داده‌ای دریافت نشد؛ اتصال را بررسی کنید.','empty'));for(const r of d.results){const row=item('div','','order');row.append(item('span',r.symbol+' · '+r.direction),item('span',money(r.price)+' USDT'));$('results').append(row)}$('errors').replaceChildren(...d.errors.map(x=>item('p',x.symbol+': '+x.error)));const s=selected;const partial=!s&&d.progress?.symbol===dropdown.value&&d.progress.stage==='enriching'?d.progress.agents:[];wallStatus(s,partial);syncDesk(d);renderDiagnostics(s?.diagnostics);renderLearning(s);$('quality').textContent=s?'Funding: '+(s.funding_rate==null?'ناموجود':s.funding_rate)+' · Open interest: '+(s.open_interest==null?'ناموجود':s.open_interest)+'\nداده‌های استفاده‌نشده یا ناموجود: '+s.missing.join(', '):'هیچ سیگنال معتبری در دسترس نیست.';$('progress').textContent=(d.progress?.completed??0)+' / '+(d.progress?.total??0)+' '+(d.progress?.symbol||'');$('activity').replaceChildren(...(d.activity||[]).map(x=>{const row=item('div','','activityrow');row.append(item('span',new Date(x.time*1000).toLocaleTimeString('fa-IR')),item('span',x.message,x.level==='error'?'negative':''));return row}));$('agent-list').replaceChildren();const failed=d.status==='error'||d.status==='stale'||d.errors.some(x=>x.symbol===dropdown.value||x.symbol==='*');const waiting=['starting','scanning'].includes(d.status)&&(d.focus===dropdown.value||d.progress?.symbol===dropdown.value);const fallback=failed?'داده معتبر دریافت نشد؛ اتصال را بررسی کنید.':waiting?'در حال دریافت داده.':'برای این ارز تحلیل را شروع کنید.';for(const [i,a] of (s?.agents||(partial?.length?partial:null)||(d.agents||[]).map(a=>({...a,status:failed?'بدون داده':waiting?'در انتظار داده':'تحلیل نشده',detail:fallback,vote:null}))).entries()){const card=item('article','','agent');card.dataset.vote=String(a.vote||0);card.dataset.phase=typeof a.vote==='number'?'done':failed?'failed':'waiting';const profile=agentProfiles[a.name]||['🔹','تحلیلگر بازار'];const top=item('div','','agenttop');const icon=item('span',profile[0],'agenticon');icon.setAttribute('aria-hidden','true');top.append(icon,item('span',a.status,'agentstate'));const specialty=item('span',profile[1],'agent-specialty');const evidence=item('div','','agent-evidence');evidence.append(item('p','بررسی تخصصی'),item('strong',a.detail));const phase=item('span',typeof a.vote==='number'?'✓ نتیجه محاسبه شد':failed?'⚠ داده در دسترس نیست':'◌ در انتظار داده معتبر','agent-phase');card.append(top,specialty,item('h4',a.role),phase,evidence);const history=s?.adaptive?.agents?.find(r=>r.name===a.name);if(history)card.append(item('small','یادگیری: '+history.correct+' رأی درست از '+history.samples));if(typeof a.vote==='number')card.append(item('small','رأی محاسباتی: '+(a.vote>0?'+':'')+a.vote));$('agent-list').append(card)}filterWall()}
async function refresh(){try{const response=await fetch('/api/scan',{cache:'no-store'});if(!response.ok)throw Error('خطای سرور');render(await response.json())}catch(e){current=null;renderWorkflow({status:'error',errors:[]},null);renderDecision(null);renderChart(null);$('price').textContent='—';$('levels').textContent='—';$('votes').textContent='—';$('results').replaceChildren(item('p','ارتباط با برنامه قطع است.','empty'));candidates.replaceChildren();$('agent-list').replaceChildren();$('quality').textContent='ارتباط پنل با سرور قطع است';qualityDetails.replaceChildren();$('system-status').textContent='آفلاین';$('system-status').dataset.state='error';$('direction').textContent='قطع ارتباط';$('brief').textContent='گزارش تازه در دسترس نیست';message('ارتباط با برنامه برقرار نشد')}}
$('analyze').disabled=false;$('analyze').title='';
$('analyze').onclick=async()=>{const button=$('analyze'),symbol=$('contract').value;if(!symbol){message('ابتدا یک قرارداد انتخاب کنید');return}button.disabled=true;button.textContent='در حال ثبت درخواست…';try{const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol})});if(!response.ok)throw Error('امکان شروع تحلیل نیست');document.body.classList.add('analysis-open');message('درخواست تحلیل ثبت شد');await refresh();workflow.scrollIntoView({block:'start',behavior:'smooth'})}catch(e){message(e.message)}finally{button.disabled=false;button.textContent='✧ شروع تحلیل این ارز'}};$('refresh').onclick=refresh;$('download').onclick=downloadHtml;refresh();setInterval(refresh,1500);

function showProfile(){
 const labels={low:'کم',moderate:'متوسط',high:'بالا'};
 if(!personalProfile){$('welcome').textContent='پایش بازار، تحلیل چندنقشی و بررسی فرصت‌های احتمالی';$('profile-result').textContent='هنوز پرسش‌نامه تکمیل نشده است.';return}
 $('welcome').textContent=personalProfile.name+'، به مرکز تحلیل خوش آمدید';
 $('profile-result').textContent='پروفایل ریسک: '+labels[personalProfile.level]+' · امتیاز '+personalProfile.score+' از '+personalProfile.max_score+(personalProfile.reasons?.length?' · احتیاط: '+personalProfile.reasons.join('؛ '):'')+' · '+personalProfile.note;
}
$('risk-form').onsubmit=async event=>{
 event.preventDefault();
 try{
  const answers=Object.fromEntries(new FormData(event.target));const name=answers.display_name.trim();delete answers.display_name;
  if(!name)throw Error('نام را وارد کنید');
  const response=await fetch('/api/risk-profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(answers)});
  if(!response.ok)throw Error('پاسخ‌ها را بررسی کنید');
  const result=await response.json();const profile={...result,name,answers};
  try{localStorage.setItem(profileKey,JSON.stringify(profile))}catch(error){throw Error('ذخیره محلی در مرورگر در دسترس نیست')}
  personalProfile=profile;showProfile();if(current)render(current);message('پروفایل ریسک ذخیره شد')
 }catch(error){message(error.message)}
};
$('profile-clear').onclick=()=>{try{localStorage.removeItem(profileKey)}catch(error){message('حذف پروفایل از مرورگر ممکن نیست');return}personalProfile=null;$('risk-form').reset();showProfile();if(current)render(current);message('پروفایل محلی پاک شد')};
if(personalProfile?.answers){for(const [key,value] of Object.entries(personalProfile.answers)){const field=$('risk-form').elements.namedItem(key);if(field)field.value=value}$('risk-form').elements.namedItem('display_name').value=personalProfile.name}
showProfile();


async function loadReports(){try{const r=await fetch('/api/reports',{cache:'no-store'});if(!r.ok)throw Error('تاریخچه در دسترس نیست');const data=await r.json();const list=$('reports-list');list.replaceChildren();if(!data.reports.length){list.append(item('p','هنوز گزارشی ثبت نشده است.','empty'));return}for(const entry of data.reports){const row=item('div','','report-row');const info=entry.report;const header=item('div','','report-header');header.append(item('strong',new Date(entry.timestamp*1000).toLocaleString('fa-IR')),item('span',(info.status==='running'?'بررسی انجام شد':'خطا')));row.append(header);const details=(info.results||[]).map(x=>x.symbol+' · '+x.direction+' · '+money(x.price)).join(' | ');row.append(item('p',details||'داده معتبر دریافت نشده است.'));for(const x of info.results||[]){if(!x.agents?.length)continue;const section=item('details','');section.append(item('summary',x.symbol+' · بررسی نقش‌ها'));for(const a of x.agents)section.append(item('p',a.role+' · '+a.detail+' ← '+a.status));row.append(section)}list.append(row)}}catch(e){$('reports-list').textContent=e.message}}
$('reports-refresh').onclick=loadReports;loadReports();setInterval(loadReports,30000);

function renderDiagnostics(d){const list=$('diagnostics-list');list.replaceChildren();if(!d||!d.agents.length){list.append(item('p','نمونه تاریخی کافی در دسترس نیست.','empty'));return}for(const a of d.agents){const row=item('div','','report-row');row.append(item('strong',a.name),item('p','تعداد رأی: '+a.samples+' · هم‌جهتی تاریخی: '+a.accuracy_pct.toFixed(1)+'٪'+(a.insufficient?' · نمونه ناکافی':'')));list.append(row)}}

function renderLearning(s){
 const box=$('learning');box.replaceChildren();
 if(!s){box.textContent='در انتظار داده بازار';return}
 const a=s.adaptive,n=s.news;
 if(a)box.append(item('p','پیشنهاد آزمایشی: '+a.direction+' · کندل‌های ارزیابی‌شده: '+a.samples+' · جهت درست امتیاز خام: '+a.correct+' از '+a.directional_samples));
 if(a?.comparison){
  const c=a.comparison;
  box.append(item('p','پیش‌بینی‌های در انتظار: '+a.pending_count+' · خارج از تاریخچه موجود: '+(a.pending_outside_history??'نامشخص')));
  box.append(item('p',a.last_settled?'آخرین کندل ارزیابی‌شده: '+new Date(a.last_settled*1000).toLocaleString('fa-IR'):'در انتظار بسته‌شدن اولین کندل هدف'));
  box.append(item('p',c.paired?'مقایسه روی '+c.paired+' کندل با رأی جهت‌دار هر دو روش: مدل تطبیقی '+c.adaptive_correct+' درست، رأی ساده '+c.baseline_correct+' درست.':'هنوز نتیجه مشترکی برای مقایسه دو روش ثبت نشده است.'));
  for(const r of a.agents){const name=s.agents.find(x=>x.name===r.name)?.role||r.name;box.append(item('p',name+' · '+r.correct+' رأی درست از '+r.samples+' · وزن فعلی '+r.weight.toFixed(3)))}
 }
 box.append(item('p',n?.available?'CoinDesk · تیتر مرتبط در ۲۴ ساعت: '+n.matched:'خبر در دسترس نیست'));
 for(const title of n?.headlines||[])box.append(item('p',title));
}
function active(){return current?.results?.find(x=>x.symbol===$('contract').value)}
function usable(s){const now=Date.now()/1000;return s&&current?.status!=='error'&&now-s.checked_at>=0&&now-s.checked_at<=900&&now-(s.last_candle+3600)>=0&&now-(s.last_candle+3600)<=4500}
function reason(s){return !usable(s)?'داده تازه کافی نیست؛ فعلاً بدون سیگنال.':s.symbol+' · '+s.direction+' · '+s.positive+' رأی مثبت و '+s.negative+' منفی. زمان بسته‌شدن کندل: '+new Date((s.last_candle+3600)*1000).toLocaleString('fa-IR')}
function syncDesk(d){if($('dialog').dataset.symbol!==$('contract').value)paintChat($('contract').value);const s=active();renderWorkflow(d,s);renderDecision(s);renderQuality(s);renderChart(s);renderCandidates(d);$('system-status').dataset.state=d.status;if(d.linkedin){const link=item('a','LinkedIn');link.href=d.linkedin;$('linkedin').replaceChildren(link)}$('brief').textContent=reason(s);let select=$('expert'),prev=select.value;select.replaceChildren(new Option('جمع‌بندی تیم',''));for(const a of s?.agents||d.agents||[])select.add(new Option(a.role,a.name));select.value=prev;startTicker($('contract').value,d.ticker_supported)}
function renderCandidates(data){
 candidates.replaceChildren(item('h4','فرصت‌های همین نوبت'),item('p','بر اساس رأی نمادهای بررسی‌شده در این نوبت.','tiny'));
 const ranked=(data.results||[]).filter(result=>usable(result)&&result.direction!=='WAIT').sort((first,second)=>Math.abs(second.votes)-Math.abs(first.votes)).slice(0,5);
 if(!ranked.length){candidates.append(item('p','نتیجه جهت‌دار تازه‌ای وجود ندارد.','empty'));return}
 for(const result of ranked){
  const button=item('button',result.symbol+' · '+result.direction+' · رأی '+result.votes+' · '+new Date(result.checked_at*1000).toLocaleTimeString('fa-IR'),'candidate');
  button.type='button';button.onclick=()=>{$('search-market').value='';fillMarkets($('contract'),current.symbols||[]);$('contract').value=result.symbol;$('contract').dispatchEvent(new Event('change'));$('contract').scrollIntoView({block:'center'})};
  candidates.append(button);
 }
}
$('contract').addEventListener('change',()=>{if(current)render(current)});
const conversations=new Map();
const chatStorageKey='ebadi-chat-history-v1';
try{const saved=JSON.parse(localStorage.getItem(chatStorageKey)||'{}');for(const [symbol,turns] of Object.entries(saved).slice(-20))if(Array.isArray(turns))conversations.set(symbol,turns.filter(m=>m&&['user','assistant'].includes(m.role)&&typeof m.content==='string'&&typeof m.label==='string').slice(-40))}catch{}
function saveChats(){try{localStorage.setItem(chatStorageKey,JSON.stringify(Object.fromEntries([...conversations.entries()].slice(-20).map(([symbol,turns])=>[symbol,turns.slice(-40)]))))}catch{message('ذخیره تاریخچه مرورگر در دسترس نیست')}}
let pendingChat=false;
function paintChat(symbol){
 const log=$('dialog');log.dataset.symbol=symbol;log.replaceChildren();
 const messages=conversations.get(symbol)||[];
 if(!messages.length)log.append(item('p','سلام! درباره تحلیل، ریسک یا اختلاف نظر تیم از من بپرسید.','chat-empty'));
 for(const m of messages){const bubble=item('div','',m.role==='user'?'chat-bubble from-user':'chat-bubble from-assistant');bubble.append(item('small',m.label),item('p',m.content));log.append(bubble)}
 log.scrollTop=log.scrollHeight;
}
$('contract').addEventListener('change',()=>paintChat($('contract').value));
$('chat-clear').onclick=()=>{conversations.delete($('contract').value);saveChats();paintChat($('contract').value)};
$('question').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('ask').requestSubmit()}});
$('chat-report').onclick=()=>{if(!pendingChat){$('question').value='یک گزارش شامل نتیجه، شواهد موافق و مخالف، ریسک و شرایط ابطال بنویس.';$('ask').requestSubmit()}};
$('ask').onsubmit=async e=>{
 e.preventDefault();if(pendingChat)return;
 const symbol=$('contract').value,q=$('question').value.trim();if(!q||!symbol)return;
 const turns=conversations.get(symbol)||[],history=turns.filter(x=>x.keep).slice(-6).map(x=>({role:x.role,content:x.content.slice(0,1600)}));
 conversations.set(symbol,turns);turns.push({role:'user',label:'شما',content:q,keep:true});
 $('question').value='';saveChats();paintChat(symbol);pendingChat=true;
 const btn=e.target.querySelector('button');btn.disabled=true;btn.textContent='در حال بررسی…';
 try{
 const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol,question:q,expert:$('expert').value,history})});
 if(!res.ok)throw Error();
 const d=await res.json();const labels={ai:'دستیار تحلیلی',local:'خلاصه محلی',no_data:'وضعیت داده',busy:'وضعیت مدل',unavailable:'وضعیت مدل',quota:'سقف روزانه'};
 const stamp=d.checked_at?' · گزارش '+new Date(d.checked_at*1000).toLocaleTimeString('fa-IR'):'';
 turns.push({role:'assistant',label:(labels[d.mode]||'پاسخ')+' · '+symbol+stamp,content:d.answer,keep:d.mode==='ai'});
 }catch{turns.push({role:'assistant',label:'خطا',content:'ارتباط با سرور میز برقرار نشد.',keep:false})}
 finally{pendingChat=false;btn.disabled=false;btn.textContent='ارسال ↑';if(turns.length>40)turns.splice(0,turns.length-40);saveChats();paintChat($('contract').value)}
};

async function refreshNews(){
 try{
  const response=await fetch('/api/news',{cache:'no-store'});if(!response.ok)throw Error();
  const data=await response.json(), list=$('news-list');list.replaceChildren();
  const states={starting:'در حال دریافت خبر…',online:'منابع متصل',partial:'بخشی از منابع در دسترس',unavailable:'دریافت خبر قطع است'};
  $('news-status').textContent=(states[data.status]||'نامشخص')+(data.checked_at?' · '+new Date(data.checked_at*1000).toLocaleTimeString('fa-IR'):'');
  if(!data.items.length){list.append(item('p','خبری دریافت نشده است.','tiny'));return}
  for(const news of data.items){
   const card=item('article','','news-item');const meta=item('div','','news-meta');
   meta.append(item('span',news.critical?'🔴 نیاز به بررسی فوری':'◉ خبر تازه',news.critical?'news-critical':''),item('span',news.source+' · '+new Date(news.published_at*1000).toLocaleString('fa-IR')));
   const link=item('a',news.title,'news-title');link.href=news.url;link.target='_blank';link.rel='noopener noreferrer';link.dir='auto';
   card.append(meta,link,item('p',news.summary||'خلاصه فارسی موجود نیست؛ تیتر اصلی را بخوانید.','news-summary'));
   if(news.impact)card.append(item('p','اثر احتمالی: '+news.impact,'tiny'));
   list.append(card);
  }
 }catch{$('news-status').textContent='ارتباط با سرور قطع است'}
}
refreshNews();setInterval(refreshNews,30000);
var stream,streamKey,lastTick=0,retryAt=0;
function clearTick(note){lastTick=0;$('tick-price').textContent='—';$('tick-status').textContent=note}
function startTicker(symbol,allowed){let key=allowed&&symbol&&symbol.endsWith('/USDT:USDT')?symbol:'';if(key===streamKey&&(stream||Date.now()<retryAt||!key))return;streamKey=key;const old=stream;stream=null;if(old)old.close();clearTick('قیمت زنده در دسترس نیست');if(!key)return;const topic='tickers.'+key.split('/')[0]+'USDT';let ws=new WebSocket('wss://stream.bybit.com/v5/public/linear');stream=ws;ws.onopen=()=>ws.send(JSON.stringify({op:'subscribe',args:[topic]}));ws.onmessage=e=>{if(stream!==ws)return;let m;try{m=JSON.parse(e.data)}catch{return}if(m.topic!==topic||!m.data?.lastPrice||Date.now()-m.ts>15000||m.ts>Date.now()+3000)return;const p=Number(m.data.lastPrice);if(p>0&&Number.isFinite(p)){lastTick=m.ts;$('tick-price').textContent=money(p)+' USDT';$('tick-status').textContent=key+' · '+new Date(lastTick).toLocaleTimeString('fa-IR')}};ws.onclose=()=>{if(stream!==ws)return;stream=null;retryAt=Date.now()+15000;clearTick('ارتباط قیمت زنده قطع است')}}
setInterval(()=>{if(lastTick&&Date.now()-lastTick>15000)clearTick('قیمت به‌روز دریافت نشده است');if(stream?.readyState===1)stream.send('{"op":"ping"}')},5000);
function downloadHtml(){if(!current)return;const doc=document.implementation.createHTMLDocument('گزارش میز معامله‌گر | ebadi');doc.documentElement.lang='fa';doc.documentElement.dir='rtl';const main=document.querySelector('main').cloneNode(true);main.querySelectorAll('form,button,.preferences,.profile-panel,.follow-panel,.choose-controls').forEach(x=>x.remove());doc.body.append(main);const meta=doc.createElement('meta');meta.charset='utf-8';doc.head.prepend(meta);const style=doc.createElement('style');style.textContent='body{font:16px/1.8 Tahoma,Arial,sans-serif;max-width:900px;margin:auto;padding:2rem;color:#252354;background:#f5f4ff}section,article{background:#fff;border:1px solid #dddafa;border-radius:14px;padding:16px;margin:12px 0}h1,h2,h3,a{color:#5641b9}small{display:block;color:#5d6384}';doc.head.append(style);doc.body.prepend(item('p','نسخه ثابت گزارش · '+new Date().toLocaleString('fa-IR')));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['<!doctype html>'+doc.documentElement.outerHTML],{type:'text/html;charset=utf-8'}));a.download='ebadi-market-report.html';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}

function fillMarkets(select,symbols){
 const q=$('search-market').value.trim().toUpperCase(), matches=symbols.filter(x=>x.includes(q)), signature=matches.join('|');
 const catalogNote=current?.catalog_status==='cached'?'فهرست ذخیره‌شده از '+new Date(current.catalog_checked_at*1000).toLocaleString('fa-IR')+'؛ وضعیت قرارداد ممکن است تغییر کرده باشد.':current?.catalog_status==='live'?'فهرست به‌روز بازار.':'فهرست اولیه؛ قراردادها هنوز تأیید نشده‌اند.';
 $('market-count').textContent='نماد در فهرست: '+symbols.length.toLocaleString('fa-IR')+' · نتیجه جست‌وجو: '+matches.length.toLocaleString('fa-IR')+' · '+(current?.catalog_order==='turnover'?'ترتیب بر اساس ارزش معاملات ۲۴ ساعته':'ترتیب پیش‌فرض؛ رتبه زنده در دسترس نیست')+' · '+catalogNote;
 if(select.dataset.markets===signature)return;
 const prev=select.value;select.replaceChildren(...matches.map(x=>new Option(x,x)));select.dataset.markets=signature;
 if(matches.includes(prev))select.value=prev;else if(matches.includes('BTC/USDT:USDT'))select.value='BTC/USDT:USDT';
}
const marketCount=item('p','','tiny');marketCount.id='market-count';$('search-market').closest('.choose-panel').append(marketCount);
$('search-market').oninput=()=>{if(current)render(current)};
function wallStatus(s,partial){
 $('wall-time').textContent=s?s.symbol+' · آخرین بررسی '+new Date(s.checked_at*1000).toLocaleTimeString('fa-IR')+' · کندل بسته '+new Date((s.last_candle+3600)*1000).toLocaleTimeString('fa-IR'):partial?.length?'تحلیل نقش‌ها آماده است؛ گزارش تکمیلی در حال دریافت است.':'گزارشی برای این ارز دریافت نشده است.';
 const f=s?.flow;
 $('wall-flow').textContent=f?'معاملات ≥ ۱۰۰ هزار USDT: '+f.count+' · خرید '+money(f.buy)+' / فروش '+money(f.sell)+' USDT · '+(f.vote>0?'غلبه خرید':f.vote<0?'غلبه فروش':'شواهد ناکافی یا متعادل'):'جریان معاملات بزرگ: داده در دسترس نیست';
}
function filterWall(){
 const mode=$('wall-filter').value,cards=[...$('agent-list').children];
 for(const c of cards){const v=Number(c.dataset.vote);c.hidden=!(mode==='all'||(mode==='up'&&v>0)||(mode==='down'&&v<0)||(mode==='neutral'&&v===0))}
 $('wall-count').textContent=cards.filter(c=>!c.hidden).length.toLocaleString('fa-IR')+' نقش نمایش داده شد';
}
$('wall-filter').onchange=filterWall;
function focusMarket(){$('search-market').focus();$('search-market').select()}
$('jump-market').onclick=focusMarket;
$('jump-chat').onclick=()=>{document.body.classList.add('analysis-open');$('question').focus()};
function openRisk(){extraDetails.open=true;$('preferences').open=true;$('preferences').querySelector('input').focus()}
$('jump-risk').onclick=openRisk;
document.querySelector('a[href="#preferences"]').addEventListener('click',()=>{extraDetails.open=true;$('preferences').open=true});
document.addEventListener('keydown',e=>{if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.target.closest('input,select,textarea,[contenteditable]')){e.preventDefault();focusMarket()}});
const deskLinks=[...document.querySelectorAll('aside nav a')];
for(const link of deskLinks)link.addEventListener('click',()=>{if(['#agents','#desk-chat'].includes(link.hash))document.body.classList.add('analysis-open')});
function highlightDesk(){let active=deskLinks[0];for(const link of deskLinks){const section=document.querySelector(link.hash);if(section&&section.getClientRects().length&&section.getBoundingClientRect().top<innerHeight*.45)active=link}for(const link of deskLinks){if(link===active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current')}}
addEventListener('scroll',highlightDesk,{passive:true});highlightDesk();
