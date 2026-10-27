"""Shared CLI/UI provider selection."""
from .workspace import DatasetWorkspace

def import_source(workspace,payload,max_bytes=512*1024**2):
    import json
    name=payload.get('dataset_name')
    if name is not None and (not isinstance(name,str) or len(name)>200):
        raise ValueError('Dataset name must be text of up to 200 characters')
    result=_import_source(workspace,payload,max_bytes)
    if name and name.strip():
        result.metadata['name']=name.strip()
        (result.directory/'dataset.json').write_text(json.dumps(result.metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

def _import_source(workspace,payload,max_bytes=512*1024**2):
    from . import sources
    ws=workspace if isinstance(workspace,DatasetWorkspace) else DatasetWorkspace(workspace)
    common={'max_bytes':max_bytes}
    source=payload.get('source','path')
    if source=='path':return ws.import_files(payload['path'],**common)
    if source=='sklearn':return sources.import_sklearn(ws,payload.get('name','iris'),**common)
    if source=='openml':return sources.import_openml(ws,int(payload['data_id']),**common)
    if source=='huggingface':return sources.import_huggingface(ws,payload['repository'],split=payload.get('split') or 'train',config=payload.get('config') or None,**common)
    if source=='kaggle':return sources.import_kaggle(ws,payload['competition'],filename=payload.get('filename') or 'train.csv',**common)
    if source=='url':return sources.import_url(ws,payload['url'],**common)
    raise ValueError('Unknown source provider')

def main(argv=None):
    import argparse
    import sys
    p=argparse.ArgumentParser(prog='eda fetch')
    p.add_argument('source',choices=['path','sklearn','openml','huggingface','kaggle','url'])
    p.add_argument('value',help='File path, dataset name, OpenML ID, Hub repository, competition slug or URL')
    p.add_argument('--workspace',default='eda-data/datasets');p.add_argument('--file',default='train.csv');p.add_argument('--split',default='train');p.add_argument('--config');p.add_argument('--max-mb',type=int,default=512)
    p.add_argument('--dataset-name');a=p.parse_args(argv);payload={'dataset_name':a.dataset_name,'source':a.source,'filename':a.file,'split':a.split,'config':a.config}
    payload[{'path':'path','sklearn':'name','openml':'data_id','huggingface':'repository','kaggle':'competition','url':'url'}[a.source]]=a.value
    try:
        d=import_source(a.workspace,payload,max_bytes=a.max_mb*1024**2)
        print('Saved dataset: '+d.dataset_id+'\nSource: '+str(d.raw_files[0]));return 0
    except (ValueError,OSError,ImportError,KeyError) as exc:print('error: '+str(exc),file=sys.stderr);return 2
