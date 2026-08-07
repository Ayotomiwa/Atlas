import re
ID_RE=re.compile(r'^[a-z0-9-]+(?:\.[a-z0-9-]+)+$')
STG_RE=re.compile(r'^STG-\d{8}-[a-z0-9-]+(?:-\d+)?$')
def valid_curated_id(value,prefix): return bool(value and value.startswith(prefix+'.') and ID_RE.fullmatch(value))
def valid_staging_id(value): return bool(value and STG_RE.fullmatch(value))
