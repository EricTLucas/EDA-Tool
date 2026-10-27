"""Plain report context and stable render slots; no workbench dependencies."""
from html import escape
import hashlib
import re


def column_id(name):
    return 'column-'+hashlib.sha256(str(name).encode()).hexdigest()[:16]


def slot(name, content=''):
    return '<!-- eda:'+name+' -->'+content+'<!-- /eda:'+name+' -->'


def apply_context(html, context=None):
    context=context or {};ai=context.get('analysis') or {};e=lambda v:escape(str(v),quote=True)
    def put(name, content):
        nonlocal html
        pattern=r'<!-- eda:'+re.escape(name)+r' -->.*?<!-- /eda:'+re.escape(name)+r' -->'
        html=re.sub(pattern,lambda _:slot(name,content),html,flags=re.S)
    summary=ai.get('summary') or context.get('explanation') or 'Explore the dataset statistics, column distributions and relationships below. No written dataset summary has been supplied.'
    put('summary','<p>'+e(summary)+'</p>'+('<p class="caption">Interpreted by '+e(context.get('model',''))+'</p>' if ai else '')+('<p class="caption">AI analysis unavailable: '+e(context['error'])+'</p>' if context.get('error') else ''))
    selected=context.get('selected_target')
    targets=ai.get('possible_targets',[])
    target='<p>'+('Selected target: '+e(selected)+'. ' if selected else 'No target selected. ')+'Recommended targets: '+(', '.join('<label class="column-link" for="choose-'+column_id(c)+'">'+e(c)+'</label>' for c in targets) or '-')+'</p>'
    put('target',target)
    for col in ai.get('columns',[]):
        put(column_id(col['name'])+'-meaning','<p>'+e(col['description'])+'</p>')
    deps=ai.get('dependencies',[])
    put('dependency-findings','<h3>Possible column dependencies</h3><ul>'+''.join('<li><a href="#dependency-'+str(i)+'">'+e(', '.join(d['columns']))+'</a> · '+e(d['kind'])+'</li>' for i,d in enumerate(deps))+'</ul>' if deps else '')
    put('dependencies','<h3>Dependency review</h3>'+''.join('<article class="column-card" id="dependency-'+str(i)+'"><h3>'+e(', '.join(d['columns']))+'</h3><p>'+e(d['reason'])+'</p><p><strong>Suggested review:</strong> '+e(d['recommendation'])+'</p></article>' for i,d in enumerate(deps)) if deps else '<p class="caption">No column dependencies suggested.</p>')
    return html
