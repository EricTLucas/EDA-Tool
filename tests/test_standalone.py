import io
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

class StandaloneTests(unittest.TestCase):
    def test_cli_ai_context_roundtrip_and_local_fallback(self):
        from eda_tool.cli import main
        from eda_tool.artifacts import load_run
        with TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'input.csv';source.write_text('amount,group\n1,a\n2,b\n3,a\n')
            context={'model':'test-model','analysis':{'summary':'Interpreted sample','columns':[{'name':'amount','description':'An amount'},{'name':'group','description':'A group'}],'possible_targets':['group'],'dependencies':[]}}
            with patch('eda_tool.intelligence.analyze_profile',return_value=context):
                self.assertEqual(main(['analyze',str(source),'--output',str(root/'run'),'--html','--ai','--quiet']),0)
            self.assertEqual(load_run(root/'run').manifest['report_context'],context)
            self.assertEqual(main(['report','--run',str(root/'run'),'--output',str(root/'copy.html')]),0)
            self.assertIn('Interpreted sample',(root/'copy.html').read_text(encoding='utf-8'))
            with patch('eda_tool.intelligence.analyze_profile',side_effect=ValueError('Test API failure')):
                self.assertEqual(main(['analyze',str(source),'--output',str(root/'failed-ai'),'--html','--ai','--quiet']),0)
            self.assertIn('Test API failure',(root/'failed-ai/report.html').read_text(encoding='utf-8'))

    def test_storage_and_provider(self):
        from eda_tool.datasets.workspace import DatasetWorkspace
        from eda_tool.datasets.fetch import import_source
        with TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.csv';source.write_text('x\n1\n2\n')
            ws=DatasetWorkspace(Path(tmp)/'data');d=ws.import_files(source)
            source.write_text('changed')
            self.assertEqual(d.raw_files[0].read_text(),'x\n1\n2\n')
            self.assertEqual(ws.get(d.dataset_id).metadata['id'],d.dataset_id)
            iris=import_source(ws,{'source':'sklearn','name':'iris'})
            self.assertEqual(iris.metadata['provenance']['provider'],'sklearn')
            with self.assertRaises(ValueError):ws.get('../escape')

    def test_ui_upload_report_reopen_and_security(self):
        from fastapi.testclient import TestClient
        from eda_tool.ui import create_app
        with TemporaryDirectory() as tmp:
            with TestClient(create_app(tmp)) as client:
                page=client.get('/');self.assertEqual(page.status_code,200)
                token=re.search('name="eda-token" content="([^"]+)"',page.text)[1];headers={'x-eda-token':token}
                self.assertEqual(client.get('/api/datasets').status_code,403)
                self.assertEqual(client.get('/api/datasets',headers={**headers,'origin':'https://evil.example'}).status_code,403)
                self.assertEqual(client.get('/',headers={'host':'evil.example'}).status_code,400)
                response=client.post('/api/upload',headers=headers,files={'file':('demo.csv',b'age,plan\n20,a\n30,b\n40,a\n','text/csv')},data={'options':'{}'})
                self.assertEqual(response.status_code,200,response.text)
                ident=response.json()['job_id']
                for _ in range(300):
                    job=client.get('/api/jobs/'+ident,headers=headers).json()
                    if job['status']!='running':break
                    time.sleep(.05)
                self.assertEqual(job['status'],'done',job)
                report=client.get(job['result']['url']);self.assertEqual(report.status_code,200);self.assertIn('column-browser',report.text)
                d=client.get('/api/datasets/'+job['result']['dataset_id'],headers=headers).json()
                self.assertEqual(len(d['preview']['rows']),3);self.assertEqual(len(d['reports']),1)
                self.assertEqual(client.get('/reports/not-a-run').status_code,404)
                self.assertEqual(client.post('/api/upload',headers=headers,files={'file':('../escape.csv',b'x\n1','text/csv')}).status_code,400)
            with TestClient(create_app(tmp)) as reopened:
                token=re.search('name="eda-token" content="([^"]+)"',reopened.get('/').text)[1]
                data=reopened.get('/api/datasets',headers={'x-eda-token':token}).json()
                self.assertEqual(len(data['datasets']),1)

    def test_core_has_no_workbench_imports(self):
        import ast
        import eda_tool
        forbidden={'etml','data','tasks','preprocessing','splitting','models','training','prediction','exporting','workflows'}
        for p in Path(eda_tool.__file__).parent.rglob('*.py'):
            tree=ast.parse(p.read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom) and not node.level and node.module:self.assertNotIn(node.module.split('.')[0],forbidden,str(p))
                if isinstance(node,ast.Import):
                    for name in node.names:self.assertNotIn(name.name.split('.')[0],forbidden,str(p))
