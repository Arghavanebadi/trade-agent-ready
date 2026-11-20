"""Fail-closed deterministic trade planning; never submits or changes orders."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Limits:
    risk_fraction: float = 0.005
    max_notional: float = 100.0
    max_daily_loss_fraction: float = 0.02
    max_positions: int = 1
    max_signal_age: int = 900
    max_reference_age: int = 3900
    max_price_deviation: float = 0.005

class Rejected(ValueError): pass

def plan(signal, *, now, equity, daily_pnl, positions, halted, reference_price, reference_time, limits=Limits()):
    def finite(value): return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
    parameters=(now,equity,daily_pnl,reference_price,reference_time,limits.risk_fraction,limits.max_notional,limits.max_daily_loss_fraction,limits.max_signal_age,limits.max_reference_age,limits.max_price_deviation)
    if not all(finite(x) for x in parameters) or equity<=0 or reference_price<=0: raise Rejected('invalid inputs')
    if not (0<limits.risk_fraction<=0.02 and 0<limits.max_daily_loss_fraction<=0.1 and limits.max_notional>0 and limits.max_signal_age>0 and limits.max_reference_age>0 and 0<limits.max_price_deviation<=0.05 and isinstance(limits.max_positions,int) and limits.max_positions>0): raise Rejected('invalid limits')
    if halted: raise Rejected('halted')
    if daily_pnl <= -equity*limits.max_daily_loss_fraction: raise Rejected('daily loss limit')
    if not isinstance(positions,int) or positions<0 or positions>=limits.max_positions: raise Rejected('position limit')
    if not isinstance(signal,dict) or signal.get('direction') not in ('LONG','SHORT'): raise Rejected('no actionable signal')
    t=signal.get('created_at'); candle=signal.get('last_candle'); price=signal.get('price'); stop=signal.get('stop'); target=signal.get('target')
    if not all(finite(x) for x in (t,candle,price,stop,target)): raise Rejected('invalid signal')
    if not (0<=now-t<=limits.max_signal_age and 0<=now-reference_time<=60 and 3600<=now-candle<=limits.max_reference_age): raise Rejected('stale or future data')
    if price<=0 or stop<=0 or target<=0 or abs(reference_price-price)/price>limits.max_price_deviation: raise Rejected('invalid or deviated price')
    if signal['direction']=='LONG' and not stop<reference_price<target: raise Rejected('invalid long levels')
    if signal['direction']=='SHORT' and not target<reference_price<stop: raise Rejected('invalid short levels')
    distance=abs(reference_price-stop)
    quantity=min(equity*limits.risk_fraction/distance,limits.max_notional/reference_price)
    if not math.isfinite(quantity) or quantity<=0: raise Rejected('invalid size')
    return {'symbol':signal.get('symbol'),'direction':signal['direction'],'reference_price':reference_price,'stop':stop,'target':target,'quantity_unrounded':quantity,'notional':quantity*reference_price,'estimated_stop_loss':quantity*distance,'execution_enabled':False,'warning':'Reference only; excludes fees, slippage, rounding, liquidation and execution uncertainty.'}
