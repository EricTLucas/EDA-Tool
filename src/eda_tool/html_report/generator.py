"""Offline, self-contained HTML gallery. Escaped text; embedded PNGs; no scripts."""
from pathlib import Path
from html import escape
from io import BytesIO
import base64
import math
import numbers
import pandas as pd
from collections.abc import Mapping
from ..artifacts.runs import SavedChart
from .context import column_id, slot, apply_context


def _text(value):
    return escape(str(value), quote=True)


def _format(value, percent=False):
    if value is None: return '-'
    if isinstance(value, numbers.Real):
        if not math.isfinite(float(value)): return '-'
        if percent: return f'{float(value):.1%}'
        if isinstance(value, numbers.Integral): return f'{int(value):,}'
        return f'{float(value):,.4g}'
    return _text(value)


def _sample(value):
    try:
        if pd.isna(value):return '-'
    except (ValueError,TypeError):pass
    return _text(value)


def _detail(value, key=''):
    if isinstance(value, Mapping):
        return '<table>'+''.join('<tr><th>'+_text(k)+'</th><td>'+_detail(v,str(k))+'</td></tr>' for k,v in value.items())+'</table>' if value else '-'
    if isinstance(value,(list,tuple)):
        return ', '.join(_detail(v) for v in value) if value else '-'
    return _format(value,percent=key.startswith('pct_') or key in {'fraction','percent_missing_cells'})


def _statistics_tabs(cid, profile):
    """CSS-only radio panels keep offline exports interactive without scripts."""
    groups = [('Statistics', {k:v for k,v in profile.items() if k not in {
        'sample_values','methods','counts','percentages','common_values','length_stats',
        'top words','top words percentages','histogram','outliers'}})]
    for label, key in [('Length statistics','length_stats'),('Outliers','outliers'),
                       ('Histogram data','histogram'),('Measurement methods','methods')]:
        if profile.get(key): groups.append((label, profile[key]))
    panels = [(label, '<tr><th>Statistic</th><th>Value</th></tr>',
               ''.join('<tr><th scope="row" class="row-number">'+_text(str(k).replace('_',' ').capitalize())+
                       '</th><td>'+_detail(v,str(k))+'</td></tr>' for k,v in data.items()))
              for label,data in groups]
    for label, key, percentage in [('Counts','counts','percentages'),('Top words','top words','top words percentages')]:
        if profile.get(key):
            panels.append((label,'<tr><th>Value</th><th>Count</th><th>Percentage</th></tr>',
                ''.join('<tr><td>'+_text(k)+'</td><td>'+_format(v)+'</td><td>'+_format(profile.get(percentage,{}).get(k),True)+'</td></tr>' for k,v in profile[key].items())))
    if profile.get('common_values'):
        panels.append(('Common values','<tr><th>Value</th><th>Count</th><th>Percentage</th></tr>',
            ''.join('<tr><td>'+_sample(row[0])+'</td><td>'+_format(row[1])+'</td><td>'+_format(row[2] if len(row)>2 else None,True)+'</td></tr>' for row in profile['common_values'])))
    controls=[]; bodies=[]; rules=[]
    for i,(label,head,body) in enumerate(panels):
        ident=cid+'-stats-'+str(i)
        controls.append('<input type="radio" name="'+cid+'-statistics" id="'+ident+'"'+(' checked' if i==0 else '')+'><label for="'+ident+'">'+label+'</label>')
        bodies.append('<div class="stats-panel '+ident+' table-wrap" tabindex="0" aria-label="'+label+'"><table><thead>'+head+'</thead><tbody>'+body+'</tbody></table></div>')
        rules.append('#'+ident+':checked~.'+ident+'{display:block}')
    return '<div class="statistics-tabs"><style>'+''.join(rules)+'</style>'+''.join(controls+bodies)+'</div>'


def _section(profile, key):
    item = profile.get(key)
    return {} if item is None else item.data


class HtmlReport:
    def __init__(self, profile, charts=(), *, title='Exploratory data analysis', max_columns=50, max_warnings=30, context=None):
        self.context = context or {}
        self.profile = profile
        self.charts = list(charts)
        self.title = title
        if max_columns < 1 or max_warnings < 1: raise ValueError('Report limits must be positive')
        if len(self.charts)>100: raise ValueError('A gallery supports at most 100 charts')
        self.max_columns, self.max_warnings = max_columns, max_warnings

    def _chart(self, chart, index):
        if isinstance(chart, SavedChart):
            image = chart.path.read_bytes()
            if not image.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError('Saved gallery images must be PNG files')
            title = chart.title
        else:
            stream = BytesIO()
            chart.figure.savefig(stream, format='png', facecolor=chart.figure.get_facecolor(), bbox_inches='tight')
            image = stream.getvalue()
            title = chart.figure.texts[0].get_text() if chart.figure.texts else chart.kind
        encoded = base64.b64encode(image).decode('ascii')
        return f'''<figure id="chart-{index}">
<img src="data:image/png;base64,{encoded}" alt="{_text(title)}" loading="eager">
</figure>'''

    def _row_viewer(self):
        views = _section(self.profile, 'row_views')
        if not views:
            return ''
        tabs, panels = [], []
        for key, label in [('first','First 10 rows'), ('middle','Middle 10 rows'), ('last','Last 10 rows')]:
            frame = views.get(key)
            if frame is None:
                continue
            checked = ' checked' if key == 'first' else ''
            tabs.append(f'<input type="radio" name="row-window" id="rows-{key}"{checked}><label for="rows-{key}">{label}</label>')
            shown = frame.iloc[:10]
            headers = '<th scope="col" class="row-number">Row</th>'+''.join(f'<th scope="col">{_text(c)}</th>' for c in shown.columns)
            body = ''.join('<tr><th scope="row" class="row-number">'+_text(index)+'</th>'+''.join(
                '<td>'+_text(value)+'</td>' for value in row)+'</tr>' for index, row in zip(shown.index, shown.itertuples(index=False,name=None)))
            if not body:
                body = f'<tr><td colspan="{len(shown.columns)+1}">No rows available</td></tr>'
            panels.append(f'<div class="row-panel rows-{key} table-wrap" tabindex="0" aria-label="{label}"><table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table></div>')
        return '<section class="row-viewer"><h2>Explore the data</h2><p class="caption">Exact source-order rows; row numbers start at 1. Windows overlap for small datasets. Scroll horizontally for all columns.</p><div class="row-tabs">'+''.join(tabs+panels)+'</div></section>'

    def render(self):
        summary = _section(self.profile, 'summary')
        columns = _section(self.profile, 'columns')
        warnings = _section(self.profile, 'warnings')
        rows = []
        for name, p in list(columns.items())[:self.max_columns]:
            unique = _format(p.get('num_unique'))
            if p.get('num_unique') is None and p.get('unique_lower_bound') is not None:
                unique = f"At least {_format(p['unique_lower_bound'])}"
            missing = _format(p.get('pct_missing'),True)
            if (p.get('pct_missing') or 0) > 0:
                missing = '<span class="quality-alert">'+missing+'</span>'
            if summary.get('rows',0) > 0 and p.get('num_unique') == summary['rows']:
                unique = '<span class="quality-alert">'+unique+'</span>'
            cells = ['<label class="column-link" for="choose-'+column_id(name)+'">'+_text(name)+'</label>', _text(p.get('type','unknown')), missing,
                     unique, _format(p.get('mean')), _format(p.get('std'))]
            rows.append('<tr>'+''.join(f'<td>{c}</td>' for c in cells)+'</tr>')
        table = ''.join(rows) or '<tr><td colspan="6">No columns available</td></tr>'
        notices = [f'{col}: {message}' for col, entries in warnings.items() for message in entries.values()]
        warning_html = ''.join(f'<p class="quality-finding">{_text(message)}</p>' for message in notices[:self.max_warnings])
        omitted = max(0,len(notices)-self.max_warnings)
        if omitted: warning_html += f'<p class="quality-finding">{omitted} additional findings omitted.</p>'
        findings = '<section id="findings"><h2>Findings & recommendations</h2><h3>Data quality findings</h3>'+(warning_html if notices else '<p>No automated quality flags were found. This does not establish that the dataset is error-free.</p>')+slot('dependency-findings')+'</section>'
        per_column={c:[] for c in list(columns)[:self.max_columns]}
        summary_charts=[];relationship_charts=[];other_charts=[]
        for i,chart in enumerate(self.charts,1):
            request=getattr(chart,'request',{}) or {};kind=getattr(chart,'kind','')
            picture=self._chart(chart,i)
            if kind in {'missing_bar','missing_matrix','overview'}:summary_charts.append(picture)
            elif request.get('x') in per_column and not any(request.get(k) for k in ('y','hue','group','color')):
                per_column[request['x']].append(picture)
            elif kind in {'association','correlation','scatter','contingency','box','violin'} or request.get('y'):
                relationship_charts.append(picture)
            else:other_charts.append(picture)
        cards=[]
        for name,p in list(columns.items())[:self.max_columns]:
            cid=column_id(name)
            middle=_section(self.profile,'row_views').get('middle')
            if middle is not None and name in middle:
                values=middle[name].iloc[:10]
                sample='<div class="sample-values"><h4>Sample values · middle '+str(len(values))+' rows</h4><div class="sample-chips">'+''.join('<span><small>Row '+_text(index)+'</small>'+_sample(value)+'</span>' for index,value in values.items())+'</div></div>'
            else:sample='<p class="caption">Middle-row samples are not available in this saved profile.</p>'
            local=warnings.get(name,{})
            local_findings=''.join('<p class="quality-finding">'+_text(v)+'</p>' for v in local.values())
            cards.append('<article class="column-card" id="'+cid+'"><h3>'+_text(name)+' <span class="caption">'+_text(p.get('type','unknown'))+'</span></h3><div class="column-summary">'+slot(cid+'-meaning','<p class="caption">No written column explanation supplied.</p>')+'</div>'+local_findings+'<div class="gallery">'+(''.join(per_column[name]) or '<p class="caption">No chart saved for this column. Regenerate the EDA to include its visualization.</p>')+'</div>'+sample+_statistics_tabs(cid,p)+'</article>')
        switches=[];rules=[]
        for i,name in enumerate(list(columns)[:self.max_columns]):
            cid=column_id(name)
            switches.append('<input class="column-switch" type="radio" name="selected-column" id="choose-'+cid+'"'+(' checked' if i==0 else '')+'><label for="choose-'+cid+'">'+_text(name)+'</label>')
            rules.append('#choose-'+cid+':checked~#'+cid+'{display:block}')
        column_cards='<div class="column-browser"><style>'+''.join(rules)+'</style>'+''.join(switches+cards)+'</div>' 
        summary_gallery='<div class="gallery">'+''.join(summary_charts)+'</div>'
        relationships='<section id="relationships"><h2>Relationships & dependencies</h2><p class="caption">Observed associations describe relationships in the data; they do not establish causation. Plot labels identify sampling and methods.</p><div class="gallery">'+''.join(relationship_charts)+'</div>'+slot('dependencies')+'</section>'
        extra='<section><h2>Additional visualizations</h2><div class="gallery">'+''.join(other_charts)+'</div></section>' if other_charts else ''
        duplicate = _format(summary.get('num_duplicates'))
        column_note = f'<p class="caption">Showing {len(rows)} of {len(columns)} columns.</p>' if len(columns)>len(rows) else ''
        html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>{_text(self.title)}</title><style>
:root{{color-scheme:dark;--bg:#080B10;--surface:#10151F;--text:#E6EAF1;--muted:#A4ADBC;--line:#29313D;--accent:#C0A1FF}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 system-ui,sans-serif}}
main{{max-width:1280px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(24px,4vw,36px);line-height:1.2;font-weight:500;overflow-wrap:anywhere;margin:8px 0 12px}}
h2{{font-size:21px;font-weight:500;margin:0 0 14px}}h3{{font-size:17px;font-weight:500;margin:0;overflow-wrap:anywhere}}
.eyebrow{{color:var(--accent);font-size:12px;letter-spacing:.15em}}.caption{{color:var(--muted);font-size:13px;margin:6px 0 12px;overflow-wrap:anywhere}}
section{{margin:32px 0}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin:24px 0}}
.stat{{background:var(--surface);padding:16px;border-radius:10px}}.stat dt{{color:var(--muted);font-size:13px}}.stat dd{{margin:8px 0 0;font-size:25px;overflow-wrap:anywhere}}
.row-panel .row-number{{white-space:nowrap;overflow-wrap:normal;word-break:normal;min-width:5ch;width:1%;max-width:none}}
.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere;max-width:300px}}th{{font-weight:500;color:var(--muted)}}
.gallery{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}figure{{margin:0;min-width:0;background:var(--surface);border-radius:12px;overflow:hidden}}img{{display:block;width:100%;height:auto}}li{{margin-bottom:6px;overflow-wrap:anywhere}}
footer{{border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12px}}@media(max-width:760px){{.gallery{{grid-template-columns:1fr}}main{{padding:24px 14px}}}}
.row-viewer{{background:var(--surface);padding:22px;border:1px solid var(--line);border-radius:14px}}.row-tabs>input{{position:absolute;opacity:0;width:1px;height:1px}}.row-tabs>label{{display:inline-block;cursor:pointer;border:1px solid var(--line);border-radius:8px;padding:8px 14px;margin:0 8px 16px 0;color:var(--muted)}}.row-tabs>input:checked+label{{background:var(--accent);color:var(--bg);border-color:var(--accent)}}.row-tabs>input:focus-visible+label{{outline:2px solid var(--text);outline-offset:3px}}.row-panel{{display:none;max-height:480px}}#rows-first:checked~.rows-first,#rows-middle:checked~.rows-middle,#rows-last:checked~.rows-last{{display:block}}.row-panel th{{position:sticky;top:0;background:var(--surface)}}.row-panel td{{min-width:100px;white-space:pre-wrap}}
@media print{{figure{{break-inside:avoid}}main{{padding:0}}.gallery{{display:block}}figure{{margin-bottom:20px}}}}
.quality-alert{{color:#ff737f;font-weight:700}}
a{{color:var(--accent);text-decoration:none;background:linear-gradient(135deg,#35274f,#182435);border:1px solid #624a83;border-radius:9px;padding:7px 12px;display:inline-block;transition:background .15s,box-shadow .15s}}a:hover,a:focus-visible{{background:#51386f;box-shadow:0 0 16px #c0a1ff40;outline:2px solid var(--accent);outline-offset:2px}}
.quality-finding{{color:#ff737f;border-left:3px solid #ff737f;padding:8px 12px;background:#ff737f0b}}
.sample-values{{margin:20px 0;padding:18px;border:1px solid var(--line);border-radius:10px}}.sample-chips{{display:flex;flex-wrap:wrap;gap:10px}}.sample-chips span{{font-size:17px;white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #4e3b69;border-radius:8px;padding:10px;max-width:100%}}.sample-chips small{{display:block;font-size:11px;color:var(--muted)}}
.column-stats>div{{min-width:140px;max-width:100%;overflow-wrap:anywhere}}.column-stats table{{font-size:12px}}.column-stats dd{{max-height:360px;overflow:auto}}.contents{{display:flex;gap:14px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid var(--line)}}
.column-browser{{border:1px solid var(--line);border-radius:14px;padding:18px;background:var(--surface)}}.column-switch{{position:absolute;opacity:0;width:1px;height:1px}}.column-browser>label,.column-link{{display:inline-block;padding:8px 13px;margin:0 6px 8px 0;border:1px solid #624a83;border-radius:8px;cursor:pointer;color:var(--accent)}}.column-switch:checked+label{{background:#45305f;color:white}}.column-switch:focus-visible+label{{outline:2px solid var(--accent)}}.column-browser>.column-card{{display:none;border:0;padding:12px 0;margin:0}}@media print{{.column-browser>.column-card{{display:block}}}}
.column-card{{margin:22px 0;padding:24px;background:var(--surface);border:1px solid var(--line);border-radius:14px;scroll-margin-top:18px}}
.column-stats{{display:flex;gap:24px;flex-wrap:wrap}}.column-stats dt{{font-size:12px;color:var(--muted)}}.column-stats dd{{margin:4px 0;font-size:18px}}
.column-summary{{font-size:19px;line-height:1.7;color:#f0e7ff;max-width:100%;margin:16px 0 22px}}.column-summary p{{margin:0}}
.statistics-tabs{{width:100%;margin-top:24px;border:1px solid var(--line);border-radius:12px;padding:16px}}.statistics-tabs>input{{position:absolute;opacity:0;width:1px;height:1px}}.statistics-tabs>label{{display:inline-block;padding:8px 13px;margin:0 6px 12px 0;border:1px solid var(--line);border-radius:8px;cursor:pointer;color:var(--muted)}}.statistics-tabs>input:checked+label{{background:#45305f;color:#f4eaff;border-color:var(--accent)}}.statistics-tabs>input:focus-visible+label{{outline:2px solid var(--accent);outline-offset:3px}}.stats-panel{{display:none;max-height:440px;overflow:auto}}.stats-panel table{{width:100%}}.stats-panel thead th{{position:sticky;top:0;background:var(--surface)}}@media print{{.statistics-tabs .stats-panel{{display:block;max-height:none}}}}
.column-card .gallery{{margin-top:18px}}.column-card h3{{color:var(--accent)}}
</style></head><body><main><header><div class="eyebrow">ETML EDA</div><h1>{_text(self.title)}</h1>
<p class="caption">ETML report</p></header>
<nav class="contents" aria-label="Report contents"><a href="#dataset-summary">Summary</a><a href="#summary-statistics">Statistics</a><a href="#findings">Findings</a><a href="#columns">Columns</a><a href="#target">Targets</a><a href="#relationships">Relationships</a><a href="#data-preview">Data preview</a></nav>
<section id="dataset-summary"><h2>Dataset summary</h2>{slot('summary')}</section>
<section id="summary-statistics"><h2>Summary statistics</h2><dl class="stats"><div class="stat"><dt>Rows</dt><dd>{_format(summary.get('rows'))}</dd></div>
<div class="stat"><dt>Columns</dt><dd>{_format(summary.get('cols'))}</dd></div>
<div class="stat"><dt>Missing cells</dt><dd>{_format(summary.get('percent_missing_cells'),True)}</dd></div>
<div class="stat"><dt>Duplicate rows</dt><dd>{duplicate}</dd></div></dl><div id="column-overview"><h2>Column overview</h2>
<div class="table-wrap"><table><thead><tr><th>Column</th><th>Role</th><th>Missing</th><th>Distinct</th><th>Mean</th><th>Std. deviation</th></tr></thead><tbody>{table}</tbody></table></div>{column_note}</div>{summary_gallery}</section>

{findings}
<section id="columns"><h2>Column summaries and visualizations</h2>{column_cards}</section>
<section id="target"><h2>Potential target columns</h2>{slot("target")}</section>
{relationships}{extra}<div id="data-preview">{self._row_viewer()}</div>
<footer>Self-contained export · no network resources or scripts · sampled counts are not population estimates.<br>
This report may contain dataset-derived values, words and plotted observations. It is not anonymized.</footer>
</main></body></html>'''
        return apply_context(html,self.context)

    def save(self, path, *, overwrite=False):
        path = Path(path)
        if path.suffix.lower() not in {'.html','.htm'}: raise ValueError('Report path must end in .html or .htm')
        content = self.render()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w' if overwrite else 'x', encoding='utf-8') as stream: stream.write(content)
        return path


def build_html_report(profile, output_dir=None, path='', *, charts=None, title=None):
    """Legacy string-returning adapter; optionally embed existing PNGs from a folder."""
    if charts is None:
        charts = []
        if output_dir is not None:
            directory = Path(output_dir).resolve()
            for image in sorted(directory.glob('*.png'))[:100]:
                if not image.resolve().is_relative_to(directory): raise ValueError('Image leaves report directory')
                charts.append(SavedChart('legacy',image,image.stem,{'method':'unknown'}))
    label = title or (Path(path).stem if isinstance(path,(str,Path)) and str(path) else 'Exploratory data analysis')
    return HtmlReport(profile,charts,title=label).render()
