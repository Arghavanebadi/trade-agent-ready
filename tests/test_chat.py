import io, json, unittest
from unittest.mock import patch
import analyst

class Chat(unittest.TestCase):
    def setUp(self):
        self.state = dict(status='running', symbols=['BTC','ETH'], results=[dict(symbol='BTC',checked_at=10000,last_candle=6300,agents=[],positive=2,negative=1,direction='WAIT')])
        self.req = dict(symbol='BTC',question='Explain')
    def test_missing_and_stale(self):
        with patch('urllib.request.urlopen') as call:
            self.assertEqual(analyst.reply(self.state,self.req,11000)['mode'],'no_data')
            self.assertEqual(analyst.reply(self.state,dict(self.req,symbol='ETH'),10000)['mode'],'no_data')
            call.assert_not_called()
    def test_model(self):
        out=dict(status='completed',output=[dict(type='message',content=[dict(type='output_text',text='analysis')])])
        with patch.dict('os.environ',XAI_API_KEY='test'),patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(out).encode())) as call:
            self.assertEqual(analyst.reply(self.state,self.req,10001)['mode'],'ai')
            payload=json.loads(call.call_args.args[0].data)
            self.assertEqual(json.loads(payload['input'][0]['content'])['current_report']['symbol'],'BTC')
    def test_optional_risk_level_and_validation(self):
        out=dict(status='completed',output=[dict(type='message',content=[dict(type='output_text',text='analysis')])])
        with patch.dict('os.environ',{'XAI_API_KEY':'test'}),patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(out).encode())) as call:
            analyst.reply(self.state,dict(self.req,risk_level='low'),10001)
            context=json.loads(json.loads(call.call_args.args[0].data)['input'][0]['content'])
            self.assertEqual(context['risk_level'],'low')
            self.assertNotIn('answers',context)
            with self.assertRaises(ValueError): analyst.reply(self.state,dict(self.req,risk_level='invalid'),10001)
    def test_no_key(self):
        with patch.dict('os.environ',XAI_API_KEY=''):
            answer=analyst.reply(self.state,self.req,10001)
            self.assertEqual(answer['mode'],'local')
            self.assertIn('قیمت کندل بسته',answer['answer'])
            self.assertIn('تضمین سود نیستند',answer['answer'])
    def test_local_report_compares_prior_closed_candle(self):
        result=dict(self.state['results'][0],price=110)
        reports=[{'symbol':'BTC','recorded_at':9000,'last_candle':2700,'price':100,'direction':'LONG'},
                 {'symbol':'ETH','recorded_at':9999,'last_candle':2700,'price':1,'direction':'SHORT'},
                 {'symbol':'BTC','recorded_at':9999,'last_candle':6300,'price':200,'direction':'SHORT'}]
        answer=analyst.local_report(result,'',reports)
        self.assertIn('گزارش تاریخی 1970-01-01 02:30 UTC',answer)
        self.assertIn('+10.00٪',answer)
        self.assertIn('داده زنده نیست',answer)
        self.assertNotIn('SHORT؛ قیمت کندل بسته 200',answer)
    def test_local_summary_keeps_opposing_evidence(self):
        agents=[{'name':str(index),'role':'positive'+str(index),'vote':1,'detail':'up'} for index in range(7)]
        agents.append({'name':'opposing','role':'opposing','vote':-1,'detail':'down'})
        result=dict(self.state['results'][0],agents=agents)
        answer=analyst.local_report(result,'')
        self.assertIn('positive0',answer)
        self.assertIn('opposing',answer)
        self.assertNotIn('positive3',answer)
    def test_local_report_rejects_invalid_or_future_historical_data(self):
        result=dict(self.state['results'][0],price=110)
        reports=[{'symbol':'BTC','recorded_at':10001,'last_candle':2700,'price':100},
                 {'symbol':'BTC','recorded_at':9000,'last_candle':float('nan'),'price':1}]
        self.assertIn('گزارش تاریخی متمایز برای مقایسه موجود نیست',analyst.local_report(result,'',reports))
        invalid=[{'symbol':'BTC','recorded_at':9000,'last_candle':2700,'price':float('nan')}]
        self.assertIn('مقایسه قیمت ناموجود است',analyst.local_report(result,'',invalid))
    def test_local_reply_includes_history(self):
        self.state['results'][0]['price']=110
        history=[{'symbol':'BTC','recorded_at':9000,'last_candle':2700,'price':100,'direction':'WAIT'}]
        with patch.dict('os.environ',{'XAI_API_KEY':'','OLLAMA_MODEL':''}):
            self.assertIn('+10.00٪',analyst.reply(self.state,self.req,10001,historical=history)['answer'])
    def test_online_conversation_does_not_send_stale_report(self):
        out=dict(status='completed',output=[dict(type='message',content=[dict(type='output_text',text='پاسخ')])])
        with patch.dict('os.environ',XAI_API_KEY='test'),patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(out).encode())) as call:
            answer=analyst.reply(self.state,self.req,11000)
            self.assertEqual(answer['mode'],'ai')
            payload=json.loads(call.call_args.args[0].data)
            self.assertIsNone(json.loads(payload['input'][0]['content'])['current_report'])
    def test_local_model_receives_historical_reports(self):
        out={'done':True,'message':{'content':'پاسخ'}}
        with patch.dict('os.environ',{'XAI_API_KEY':'','OLLAMA_MODEL':'test'}),patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(out).encode())) as call:
            answer=analyst.reply(self.state,self.req,10001,historical=[{'symbol':'BTC','recorded_at':9000}])
            self.assertEqual(answer['mode'],'ai')
            payload=json.loads(call.call_args.args[0].data)
            self.assertEqual(json.loads(payload['messages'][1]['content'])['historical_reports'][0]['recorded_at'],9000)
            self.assertEqual(call.call_args.args[0].full_url,'http://127.0.0.1:11434/api/chat')
