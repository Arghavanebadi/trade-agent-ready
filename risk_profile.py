"""Transparent questionnaire classification; not financial advice or account verification."""
OPTIONS={'horizon':('under_1y','one_to_three','over_three'),'experience':('none','some','experienced'),'loss':('five','ten','twenty'),'capacity':('essential','limited','surplus'),'emergency':('no','yes')}
EXTRA_OPTIONS={'leverage_experience':('none','some','experienced'),'borrowed_funds':('yes','no'),'loss_response':('exit','wait','plan')}

def assess(answers):
 if not isinstance(answers,dict) or not set(OPTIONS)<=set(answers) or set(answers)-set(OPTIONS)-set(EXTRA_OPTIONS) or any(answers[k] not in choices for k,choices in OPTIONS.items()) or any(k in answers and answers[k] not in choices for k,choices in EXTRA_OPTIONS.items()): raise ValueError('invalid questionnaire')
 points={'horizon':{'under_1y':0,'one_to_three':1,'over_three':2},'experience':{'none':0,'some':1,'experienced':2},'loss':{'five':0,'ten':1,'twenty':2},'capacity':{'essential':0,'limited':1,'surplus':2},'emergency':{'no':0,'yes':1}}
 score=sum(points[k][answers[k]] for k in OPTIONS)
 # A lack of loss capacity or emergency buffer overrides a high preference score.
 reasons=[]
 if answers['capacity']=='essential': reasons.append('سرمایه برای هزینه‌های ضروری لازم است')
 if answers['emergency']=='no': reasons.append('ذخیره اضطراری جداگانه وجود ندارد')
 if answers.get('borrowed_funds')=='yes': reasons.append('استفاده از سرمایه قرضی اعلام شده است')
 if answers.get('leverage_experience')=='none': reasons.append('تجربه معاملات اهرمی اعلام نشده است')
 if answers.get('loss_response')=='exit': reasons.append('واکنش به زیان، خروج فوری است')
 if reasons: level='low'
 elif score<=3: level='low'
 elif score<=6: level='moderate'
 else: level='high'
 return {'level':level,'score':score,'max_score':9,'reasons':reasons,'rule':'low when a conservative override applies; otherwise 0–3 low, 4–6 moderate, 7–9 high','note':'پرسش‌نامه تخمینی است، مناسب‌بودن فیوچرز را تأیید نمی‌کند و به معامله متصل نیست.'}
