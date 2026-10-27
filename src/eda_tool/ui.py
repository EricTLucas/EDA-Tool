"""Loopback-only standalone EDA browser application."""
from pathlib import Path
from tempfile import TemporaryDirectory
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import json
import os
import secrets
import threading
import uuid


def create_app(root='eda-data',max_bytes=512*1024**2):
    try:
        from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
        from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
        from starlette.middleware.trustedhost import TrustedHostMiddleware
    except ImportError as exc:raise ImportError('Install UI support: python -m pip install -e ".[ui]"') from exc
    from .datasets.workspace import DatasetWorkspace
    from .datasets.fetch import import_source
    from .loader import open_dataset
    from .profiler import ProfileConfig
    from .workflows import run_eda
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    workspace=DatasetWorkspace(root/'datasets');runs=root/'runs';runs.mkdir(exist_ok=True)
    token=secrets.token_urlsafe(32);jobs={};pool=ThreadPoolExecutor(max_workers=1);lock=threading.Lock()
    credentials={'key':None,'invalid':False,'revision':0}
    @asynccontextmanager
    async def lifespan(app):
        yield
        pool.shutdown(wait=True,cancel_futures=True)
    app=FastAPI(title='ETML EDA',lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])
    @app.middleware('http')
    async def protect(request: Request,call_next):
        if request.url.path.startswith('/api/'):
            origin=request.headers.get('origin')
            if origin and origin!=str(request.base_url).rstrip('/'):
                return JSONResponse({'detail':'Same-origin requests only'},status_code=403)
            if not secrets.compare_digest(request.headers.get('x-eda-token',''),token):
                return JSONResponse({'detail':'Reload the EDA page to start a session'},status_code=403)
            try:length=int(request.headers.get('content-length','0'))
            except ValueError:return JSONResponse({'detail':'Invalid content length'},status_code=400)
            if length>max_bytes+1024**2:return JSONResponse({'detail':'Upload exceeds size limit'},status_code=413)
        return await call_next(request)
    static=Path(__file__).parent/'web_static'
    app.mount('/static',StaticFiles(directory=static),name='static')
    @app.get('/',response_class=HTMLResponse)
    def home():return HTMLResponse((static/'index.html').read_text(encoding='utf-8').replace('__TOKEN__',token),headers={'Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; style-src 'self'; script-src 'self'; frame-src 'self'; frame-ancestors 'none'; object-src 'none'"})
    def key_status():
        configured=bool(credentials['key'] or os.environ.get('OPENAI_API_KEY','').strip())
        return {'configured':configured,'needs_key':not configured or credentials['invalid'],
                'source':'session' if credentials['key'] else 'environment' if configured else None,
                'invalid':credentials['invalid']}
    @app.get('/api/ai-key')
    def get_key_status():return JSONResponse(key_status(),headers={'Cache-Control':'no-store'})
    @app.post('/api/ai-key')
    def set_key(payload:dict):
        key=payload.get('key')
        if key is not None and (not isinstance(key,str) or not key.strip() or len(key)>1024 or any(c.isspace() for c in key.strip())):
            raise HTTPException(400,'Enter a nonempty API key without spaces')
        credentials.update(key=key.strip() if key else None,invalid=False,revision=credentials['revision']+1)
        return JSONResponse(key_status(),headers={'Cache-Control':'no-store'})
    def submit(function):
        with lock:
            if any(j['status']=='running' for j in jobs.values()):raise HTTPException(409,'An analysis is running. Wait for it to finish.')
            ident=uuid.uuid4().hex;jobs[ident]={'status':'running','message':'Starting…'}
        def work():
            try:jobs[ident].update(status='done',result=function(jobs[ident]))
            except Exception as exc:jobs[ident].update(status='failed',error=str(exc))
        pool.submit(work);return {'job_id':ident}
    def reports(dataset_id):
        found=[]
        for p in runs.glob('*/ui.json'):
            meta=json.loads(p.read_text(encoding='utf-8'))
            if meta['dataset_id']==dataset_id:found.append(meta)
        return sorted(found,key=lambda m:m['created'],reverse=True)
    @app.get('/api/datasets')
    def datasets():return {'datasets':[d.metadata for d in workspace.list()],'max_bytes':max_bytes}
    @app.get('/api/datasets/{ident}')
    def dataset(ident:str):
        try:
            d=workspace.get(ident);source=open_dataset(d.raw_files)
            iterator=iter(source.iter_batches(batch_size=10))
            try:frame=next(iterator,None)
            finally:
                close=getattr(iterator,'close',None)
                if close:close()
            return {'dataset':d.metadata,'reports':reports(ident),'preview':{'columns':list(frame.columns),'rows':json.loads(frame.head(10).to_json(orient='values',date_format='iso'))} if frame is not None else {'columns':[],'rows':[]}}
        except (ValueError,OSError) as exc:raise HTTPException(400,str(exc))
    def analyze(d,payload,job):
        from datetime import datetime,timezone
        roles=payload.get('roles',{})
        config=ProfileConfig(batch_size=int(payload.get('batch_size',50000)),sample_size=int(payload.get('sample_size',10000)),roles=roles,categorical_threshold=int(payload.get('categorical_threshold',10)))
        ident='run-'+uuid.uuid4().hex
        key_revision=credentials['revision'];api_key=credentials['key'] or os.environ.get('OPENAI_API_KEY','').strip()
        result=run_eda(d.raw_files,output_dir=runs/ident,export_html=True,generate_summary=True,
            profile_config=config,title=d.metadata['name'],ai_api_key=api_key,ai=payload.get('ai') is True,
            ai_samples=payload.get('ai_samples') is True,explanation=payload.get('explanation',''),
            progress=lambda e:job.update(message=e.message),save_sample=payload.get('save_sample') is True)
        try:
            if payload.get('ai') is True and key_revision==credentials['revision']:
                credentials['invalid']=result.manifest.get('ai_error_kind')=='authentication'
            info={'id':ident,'dataset_id':d.dataset_id,'created':datetime.now(timezone.utc).isoformat(),'url':'/reports/'+ident,'ai_error':result.manifest.get('ai_error'),'rows':result.profile['summary'].data['rows'],'settings':{k:payload[k] for k in ('explanation','ai','ai_samples','save_sample','batch_size','sample_size','categorical_threshold','roles') if k in payload}}
            (runs/ident/'ui.json').write_text(json.dumps(info),encoding='utf-8');return info
        finally:result.close()
    @app.post('/api/import')
    def import_data(payload:dict):
        def work(job):
            job['message']='Importing dataset…';d=import_source(workspace,payload,max_bytes)
            try:return analyze(d,payload,job)
            except Exception as exc:return {'dataset_id':d.dataset_id,'warning':'Raw data saved; analysis failed: '+str(exc)}
        return submit(work)
    @app.post('/api/upload')
    def upload(file:UploadFile=File(...),options:str=Form('{}')):
        try:
            payload=json.loads(options)
            if not isinstance(payload,dict):raise ValueError('Invalid upload options')
            from .datasets.manifest import validate_filename
            name=validate_filename(file.filename or '')
            with TemporaryDirectory() as temp:
                target=Path(temp)/name;size=0
                with target.open('wb') as out:
                    while chunk:=file.file.read(1024**2):
                        size+=len(chunk)
                        if size>max_bytes:raise ValueError('Upload exceeds byte limit')
                        out.write(chunk)
                name=payload.get('dataset_name')
                if name is not None and (not isinstance(name,str) or len(name)>200):raise ValueError('Dataset name must be text of up to 200 characters')
                d=workspace.import_files(target,name=name,max_bytes=max_bytes)
            return submit(lambda job:analyze(d,payload,job))
        except (ValueError,OSError) as exc:raise HTTPException(400,str(exc))
        finally:file.file.close()
    @app.post('/api/datasets/{ident}/analyze')
    def rerun(ident:str,payload:dict):
        try:d=workspace.get(ident)
        except (ValueError,OSError) as exc:raise HTTPException(404,str(exc))
        return submit(lambda job:analyze(d,payload,job))
    @app.get('/api/jobs/{ident}')
    def job(ident:str):
        if ident not in jobs:raise HTTPException(404,'Job not found')
        return jobs[ident]
    @app.get('/reports/{ident}')
    def report(ident:str):
        import re
        if not re.fullmatch(r'run-[a-f0-9]{32}',ident) or not (runs/ident/'report.html').is_file():raise HTTPException(404,'Report not found')
        return FileResponse(runs/ident/'report.html',media_type='text/html',headers={'Content-Security-Policy':"default-src 'none'; img-src data:; style-src 'unsafe-inline'; frame-ancestors 'self'; base-uri 'none'",'X-Content-Type-Options':'nosniff'})
    return app


def main(argv=None):
    import argparse
    import webbrowser
    p=argparse.ArgumentParser(prog='eda ui');p.add_argument('--data-dir',default='eda-data');p.add_argument('--port',type=int,default=8765);p.add_argument('--max-upload-mb',type=int,default=512);p.add_argument('--no-open',action='store_true');a=p.parse_args(argv)
    if not 1<=a.port<=65535 or a.max_upload_mb<1:p.error('Use a valid port and positive upload limit')
    try:
        import uvicorn
        app=create_app(a.data_dir,a.max_upload_mb*1024**2)
    except ImportError as exc:print(str(exc));return 2
    if not a.no_open:threading.Timer(1.5,lambda:webbrowser.open('http://127.0.0.1:'+str(a.port))).start()
    uvicorn.run(app,host='127.0.0.1',port=a.port);return 0
