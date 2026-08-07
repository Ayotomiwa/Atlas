import re
ID_RE=re.compile(r'^atlas\.[a-z0-9-]+\.[a-z0-9-]+(?:\.[a-z0-9-]+){1,2}$')

def valid_id(value): return isinstance(value,str) and bool(ID_RE.match(value))
