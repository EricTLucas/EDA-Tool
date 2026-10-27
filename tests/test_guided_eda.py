import unittest
import pandas as pd
from tempfile import TemporaryDirectory
from pathlib import Path
from eda_tool.workflows import run_eda
from eda_tool.html_report import HtmlReport
from eda_tool.html_report.context import column_id, apply_context
from eda_tool.artifacts.runs import load_run

class GuidedReportTests(unittest.TestCase):
    def test_layout_context_plots_and_roundtrip(self):
        frame=pd.DataFrame({'amount':range(30),'outcome':['yes','no']*15})
        context={'model':'test','selected_target':'outcome','analysis':{
            'summary':'Example <unsafe>','columns':[{'name':'amount','description':'Amount description'},{'name':'outcome','description':'Outcome description'}],
            'possible_targets':['outcome'],'dependencies':[{'columns':['amount','outcome'],'kind':'other','reason':'Possible relation','recommendation':'Review association','drop_candidates':[]}]}}
        with TemporaryDirectory() as tmp:
            result=run_eda(frame,output_dir=Path(tmp)/'run',export_html=True,report_context=context,
                chart_requests=[{'kind':'histogram','x':'amount'},{'kind':'pie','x':'outcome'}],title='Example dataset')
            try:
                html=result.html
                headings=['Dataset summary','Summary statistics','Target &amp; modeling context']
                self.assertLess(html.index('<h2>Dataset summary'),html.index('<h2>Summary statistics'))
                self.assertLess(html.index('<h2>Column summaries and visualizations'),html.index('<h2>Potential target columns'))
                self.assertLess(html.index('<h2>Column overview'),html.index('<h2>Findings & recommendations'))
                self.assertLess(html.index('<h2>Column overview'),html.index('<h2>Relationships & dependencies'))
                self.assertEqual(html.count('<figure '),2)
                self.assertIn('Example &lt;unsafe&gt;',html)
                amount=html.split('id="'+column_id('amount')+'"')[1].split('</article>')[0]
                self.assertIn('Amount description',amount);self.assertIn('<figure',amount)
                self.assertIn('Sample values · middle 10 rows',amount)
                self.assertIn('Row 11',amount)
                self.assertIn('Interpreted by test',html)
                self.assertNotIn('AI column interpretation',html)
                self.assertNotIn('Unavailable',html)
                self.assertIn('Possible relation',html);self.assertNotIn('Preprocessing history',html)
                self.assertEqual(apply_context(html,context),html)
                saved=load_run(result.output_dir)
                restored=HtmlReport(saved.profile,saved.charts,title='Example dataset',context=saved.manifest['report_context']).render()
                self.assertIn('Amount description',restored);self.assertEqual(restored.count('<figure '),2)
            finally:result.close()

    def test_empty_context_and_hostile_column(self):
        result=run_eda(pd.DataFrame({'<script>':[1,2]}),chart_requests=[],generate_summary=False)
        try:
            html=HtmlReport(result.profile).render()
            self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html)
            self.assertIn('No target selected',html)
        finally:result.close()

    def test_all_displayed_columns_have_embedded_images(self):
        import base64,re
        from PIL import Image
        from io import BytesIO
        frame=pd.DataFrame({f'feature_{i}':range(30) for i in range(15)})
        result=run_eda(frame,export_html=True,generate_summary=True)
        try:
            html=result.html
            for name in frame:
                card=html.split('id="'+column_id(name)+'"')[1].split('</article>')[0]
                encoded=re.search(r'src="data:image/png;base64,([^"]+)"',card)
                self.assertIsNotNone(encoded,name)
                with Image.open(BytesIO(base64.b64decode(encoded[1]))) as img:
                    self.assertGreater(img.width,100);self.assertGreater(img.height,100)
                self.assertIn('Skew',card)
                self.assertIn('Measurement methods',card)
        finally:result.close()
