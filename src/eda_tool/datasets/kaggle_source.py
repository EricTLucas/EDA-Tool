"""Import a selected competition file using the user's authenticated Kaggle CLI."""
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import re
import shutil
import subprocess
import sysconfig
import zipfile


def import_kaggle(workspace, competition, *, filename='train.csv', dataset_id=None,
                  max_bytes=512*1024**2):
    from .sources import _workspace, _limits
    from eda_tool.loader import open_dataset
    _limits(1,max_bytes)
    if not isinstance(competition,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,199}',competition):
        raise ValueError('Enter the competition slug, such as titanic (not its URL).')
    if not isinstance(filename,str) or not filename or '\\' in filename:
        raise ValueError('Enter a competition data filename, such as train.csv.')
    member=PurePosixPath(filename)
    if member.is_absolute() or any(p in {'..','.'} or ':' in p for p in filename.split('/')) or filename.startswith('-'):
        raise ValueError('Invalid competition filename')
    if member.suffix.lower() not in {'.csv','.tsv','.parquet','.json','.jsonl','.ndjson'}:
        raise ValueError('Choose a CSV, TSV, Parquet, JSON or JSONL file inside the competition.')
    scripts=Path(sysconfig.get_path('scripts'))
    executable=next((str(scripts/n) for n in ('kaggle.exe','kaggle') if (scripts/n).is_file()),None) or shutil.which('kaggle')
    if not executable:
        raise ValueError('Install Kaggle support: python -m pip install -e ".[kaggle]". Then configure Kaggle authentication.')
    with TemporaryDirectory(prefix='etml-kaggle-') as temp:
        root=Path(temp)
        try:
            result=subprocess.run([executable,'competitions','download',competition,'-f',filename,'-p',str(root),'-q'],
                capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600,shell=False)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('Kaggle download timed out after 10 minutes. Try again or download the file manually.') from exc
        if result.returncode:
            # Do not expose CLI output: authentication failures can contain credentials.
            raise ValueError('Kaggle download failed. Check your CLI authentication, competition name and filename, and accept the competition rules on Kaggle. Run kaggle competitions files '+competition+' to inspect available files.')
        direct=root.joinpath(*member.parts)
        if not direct.is_file():
            archives=list(root.rglob('*.zip'))
            matches=[]
            for archive in archives:
                if archive.stat().st_size>max_bytes:raise ValueError('Downloaded archive exceeds the import size limit')
                with zipfile.ZipFile(archive) as z:
                    for info in z.infolist():
                        if info.filename==filename or (len(member.parts)==1 and info.filename==member.name):
                            matches.append((archive,info))
            if len(matches)!=1:raise ValueError('Kaggle did not return the selected data file. Check its exact filename.')
            archive,info=matches[0]
            if info.file_size>max_bytes:raise ValueError('Uncompressed file exceeds the import size limit')
            direct.parent.mkdir(parents=True,exist_ok=True)
            with zipfile.ZipFile(archive) as z,z.open(info) as src,direct.open('wb') as out:
                size=0
                while chunk:=src.read(1024**2):
                    size+=len(chunk)
                    if size>max_bytes:raise ValueError('Uncompressed file exceeds the import size limit')
                    out.write(chunk)
        if direct.is_symlink() or not direct.resolve().is_relative_to(root.resolve()):
            raise ValueError('Downloaded file leaves the download directory')
        if direct.stat().st_size>max_bytes:raise ValueError('Downloaded file exceeds the import size limit')
        open_dataset(direct).schema()
        return _workspace(workspace).import_files(direct,name=competition+' — '+member.name,
            dataset_id=dataset_id,max_bytes=max_bytes,
            provenance={'provider':'kaggle','competition':competition,'file':filename})
