"""Transparent questionnaire classification; not financial advice or account verification."""
OPTIONS={'horizon':('under_1y','one_to_three','over_three'),'experience':('none','some','experienced'),'loss':('five','ten','twenty'),'capacity':('essential','limited','surplus'),'emergency':('no','yes')}

def assess(answers):
 if not isinstance(answers,dict) or set(answers)!=set(OPTIONS) or any(answers[k] not in choices for k,choices in OPTIONS.items()): raise ValueError('invalid questionnaire')
 points={'horizon':{'under_1y':0,'one_to_three':1,'over_three':2},'experience':{'none':0,'some':1,'experienced':2},'loss':{'five':0,'ten':1,'twenty':2},'capacity':{'essential':0,'limited':1,'surplus':2},'emergency':{'no':0,'yes':1}}
 score=sum(points[k][answers[k]] for k in OPTIONS)
 # A lack of loss capacity or emergency buffer overrides a high preference score.
 if answers['capacity']=='essential' or answers['emergency']=='no': level='low'
 elif score<=3: level='low'
 elif score<=6: level='moderate'
 else: level='high'
 return {'level':level,'score':score,'max_score':9,'rule':'low when essential funds or no emergency reserve; otherwise 0–3 low, 4–6 moderate, 7–9 high','note':'پرسش‌نامه تخمینی است، مناسب‌بودن فیوچرز را تأیید نمی‌کند و به معامله متصل نیست.'}
