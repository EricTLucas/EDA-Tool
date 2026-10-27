import os,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from eda_tool.cli import main,parser

class SimpleCliTests(unittest.TestCase):
 def test_defaults_and_overrides(self):
  with patch.dict(os.environ,{'OPENAI_API_KEY':'fake'}):
   args=parser(shortcut=True).parse_args(['analyze','data.csv'])
   self.assertTrue(args.ai);self.assertTrue(args.open);self.assertTrue(args.html)
   args=parser(shortcut=True).parse_args(['analyze','data.csv','--noai','--no-open','-o','out'])
   self.assertFalse(args.ai);self.assertFalse(args.open);self.assertEqual(args.output,'out')
  with patch.dict(os.environ,{},clear=True):self.assertFalse(parser(shortcut=True).parse_args(['analyze','data.csv']).ai)
 def test_file_and_directory_shortcuts(self):
  with TemporaryDirectory() as temp:
   root=Path(temp);data=root/'input';data.mkdir();source=data/'demo.csv';source.write_text('x,y\n1,a\n2,b\n')
   for source_arg in [source,data]:
    with patch('eda_tool.cli.Path.cwd',return_value=root),patch('webbrowser.open') as browser:
     self.assertEqual(main([str(source_arg),'--noai','--no-open','--quiet','--max-charts','1']),0)
     browser.assert_not_called()
   runs=list((root/'eda-output').iterdir());self.assertEqual(len(runs),2)
   for run in runs:
    html=(run/'report.html').read_text(encoding='utf-8')
    self.assertIn('class="row-number">Row</th>',html)
    self.assertIn('white-space:nowrap;overflow-wrap:normal;word-break:normal',html)
   with patch('webbrowser.open') as browser:
    self.assertEqual(main([str(source),'--noai','-o',str(root/'custom'),'--name','My report','--quiet','--max-charts','1']),0)
    browser.assert_called_once()
   self.assertIn('My report',(root/'custom/report.html').read_text(encoding='utf-8'))
