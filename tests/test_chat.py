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
    def test_no_key(self):
        with patch.dict('os.environ',XAI_API_KEY=''):
            answer=analyst.reply(self.state,self.req,10001)
            self.assertEqual(answer['mode'],'local')
            self.assertIn('قیمت کندل بسته',answer['answer'])
            self.assertIn('تضمین سود نیستند',answer['answer'])
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
