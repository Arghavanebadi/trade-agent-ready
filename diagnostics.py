"""Historical diagnostic of existing directional votes; no training or execution."""
import research

def evaluate_votes(rows):
 errors=research.validate(rows)
 if errors: raise ValueError('invalid market data: '+'; '.join(errors))
 counts={}
 # At each close use only bars known then; score against next closed bar.
 for end in range(research.MIN_BARS,len(rows)):
  current=research.evaluate(rows[:end])
  change=rows[end]['close']-rows[end-1]['close']
  if change==0: continue
  for agent in current['agents']:
   vote=agent['vote']
   if vote not in (-1,1): continue
   record=counts.setdefault(agent['name'],{'name':agent['name'],'samples':0,'correct':0})
   record['samples']+=1
   if (vote>0 and change>0) or (vote<0 and change<0): record['correct']+=1
 results=[]
 for value in counts.values():
  n=value['samples'];results.append({**value,'accuracy_pct':100*value['correct']/n,'insufficient':n<30})
 return {'horizon':'next_closed_1h_bar','windows':max(0,len(rows)-research.MIN_BARS),'agents':results,'training':False,'strategy_modified':False,'note':'Historical directional agreement only, excluding neutral/unchanged periods; overlapping samples, costs and executions not included. Not predictive accuracy or profitability.'}
