import re
CURATED_ID_RE=re.compile(r'^[a-z][a-z0-9-]*(?:\.[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?)+$')
STAGING_ID_RE=re.compile(r'^STG-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*(?:-\d+)?$')

def valid_curated_id(value,prefix):
    return isinstance(value,str) and value.startswith(prefix+'.') and bool(CURATED_ID_RE.fullmatch(value))
def valid_staging_id(value): return isinstance(value,str) and bool(STAGING_ID_RE.fullmatch(value))
