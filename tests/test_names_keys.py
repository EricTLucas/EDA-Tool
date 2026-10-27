import json,os,re,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from fastapi.testclient import TestClient
from eda_tool.ui import create_app
from eda_tool.datasets.workspace import DatasetWorkspace
from eda_tool.intelligence import request_summary,AIAuthenticationError

class NamesKeysTests(unittest.TestCase):
 def test_names(self):
  from eda_tool.datasets.fetch import import_source
  with TemporaryDirectory() as tmp:
   p=Path(tmp)/'original.csv';p.write_text('x\n1\n2\n')
   ws=DatasetWorkspace(Path(tmp)/'data')
   self.assertEqual(ws.import_files(p).metadata['name'],'original.csv')
   d=import_source(ws,{'path':str(p),'dataset_name':' My data '})
   self.assertEqual(d.metadata['name'],'My data');self.assertEqual(d.raw_files[0].name,'original.csv')
 def test_auth_errors(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaises(AIAuthenticationError):request_summary({})
  for code in [401,429]:
   with patch('eda_tool.intelligence.urlopen',side_effect=HTTPError('url',code,'secret body',None,None)):
    with self.assertRaises(ValueError) as caught:request_summary({},api_key='fake-key')
    self.assertEqual(isinstance(caught.exception,AIAuthenticationError),code==401)
    self.assertNotIn('secret',str(caught.exception))
 def test_key_session_and_upload_auth_fallback(self):
  secret='fake-test-credential'
  with TemporaryDirectory() as tmp,patch.dict(os.environ,{},clear=True):
   with TestClient(create_app(tmp)) as c:
    token=re.search('name="eda-token" content="([^"]+)"',c.get('/').text)[1];h={'x-eda-token':token}
    self.assertTrue(c.get('/api/ai-key',headers=h).json()['needs_key'])
    self.assertEqual(c.post('/api/ai-key',json={'key':secret}).status_code,403)
    response=c.post('/api/ai-key',headers=h,json={'key':secret})
    self.assertNotIn(secret,response.text);self.assertFalse(response.json()['needs_key'])
    with patch('eda_tool.intelligence.analyze_profile',side_effect=AIAuthenticationError('Key rejected')) as mock:
     r=c.post('/api/upload',headers=h,files={'file':('test.csv',b'x\n1\n2\n')},data={'options':json.dumps({'dataset_name':'Custom name','ai':True})})
     for _ in range(600):
      job=c.get('/api/jobs/'+r.json()['job_id'],headers=h).json()
      if job['status']!='running':break
      time.sleep(.05)
     self.assertEqual(job['status'],'done',job);self.assertEqual(mock.call_args.kwargs['api_key'],secret)
    self.assertTrue(c.get('/api/ai-key',headers=h).json()['invalid'])
    report=c.get(job['result']['url']).text;self.assertIn('Custom name',report)
    self.assertNotIn(secret,report)
    for p in Path(tmp).rglob('*.json'):self.assertNotIn(secret,p.read_text(encoding='utf-8'))
    self.assertFalse(c.post('/api/ai-key',headers=h,json={'key':'replacement'}).json()['invalid'])
   with TestClient(create_app(tmp)) as c:
    token=re.search('name="eda-token" content="([^"]+)"',c.get('/').text)[1]
    self.assertFalse(c.get('/api/ai-key',headers={'x-eda-token':token}).json()['configured'])
   with patch.dict(os.environ,{'OPENAI_API_KEY':'environment-key'}),TestClient(create_app(tmp)) as c:
    token=re.search('name="eda-token" content="([^"]+)"',c.get('/').text)[1]
    self.assertEqual(c.get('/api/ai-key',headers={'x-eda-token':token}).json()['source'],'environment')
