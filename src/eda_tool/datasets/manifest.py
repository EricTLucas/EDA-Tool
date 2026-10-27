from pathlib import Path

def validate_filename(name):
    if not isinstance(name,str) or not name or name in {'.','..'} or any(c in name for c in '/\\:') or Path(name).name!=name:
        raise ValueError('Use a plain filename')
    return name
