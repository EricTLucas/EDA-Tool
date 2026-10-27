"""EDA-only raw dataset snapshots; no task or model dependencies."""
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import dataclass
import json
import re
import uuid
from .manifest import validate_filename

@dataclass
class Dataset:
    dataset_id: str
    directory: Path
    metadata: dict
    @property
    def raw_files(self):return [self.directory/'raw'/name for name in self.metadata['files']]

class DatasetWorkspace:
    def __init__(self,root):self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
    def get(self,ident):
        if not re.fullmatch(r'[A-Za-z0-9_-]+',ident):raise ValueError('Invalid dataset ID')
        folder=self.root/ident
        metadata=json.loads((folder/'dataset.json').read_text(encoding='utf-8'))
        for name in metadata['files']:validate_filename(name)
        return Dataset(ident,folder,metadata)
    def list(self):
        return [self.get(p.parent.name) for p in sorted(self.root.glob('*/dataset.json'))]
    def import_files(self,files,*,name=None,dataset_id=None,max_bytes=512*1024**2,provenance=None):
        from ..loader import open_dataset
        files=[Path(files)] if isinstance(files,(str,Path)) else [Path(p) for p in files]
        ident=dataset_id or 'data-'+uuid.uuid4().hex[:12]
        if not re.fullmatch(r'[A-Za-z0-9_-]+',ident):raise ValueError('Invalid dataset ID')
        if type(max_bytes) is not int or max_bytes<1:raise ValueError('Invalid byte limit')
        destination=self.root/ident
        if destination.exists():raise ValueError('Dataset ID already exists')
        names=[validate_filename(p.name) for p in files]
        if len(set(names))!=len(names) or not names:raise ValueError('Provide unique dataset filenames')
        with TemporaryDirectory(prefix='.import-',dir=self.root) as temp:
            staging=Path(temp);(staging/'raw').mkdir();size=0
            for path in files:
                with path.open('rb') as src,(staging/'raw'/path.name).open('wb') as dst:
                    while chunk:=src.read(1024**2):
                        size+=len(chunk)
                        if size>max_bytes:raise ValueError('Dataset exceeds the import byte limit')
                        dst.write(chunk)
            open_dataset([staging/'raw'/n for n in names]).schema()
            metadata={'id':ident,'name':name.strip() if isinstance(name,str) and name.strip() else files[0].name,'files':names,'bytes':size,'provenance':provenance or {}}
            (staging/'dataset.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
            staging.rename(destination)
        return self.get(ident)
    def import_presplit(self,*args,**kwargs):
        raise ValueError('Standalone EDA imports one partition at a time. Select a single source split.')
