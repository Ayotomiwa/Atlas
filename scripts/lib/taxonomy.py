from pathlib import Path
import yaml

def load_yaml(path: Path):
    with path.open(encoding='utf-8') as f: return yaml.safe_load(f)

def load_types(root: Path):
    items=load_yaml(root/'taxonomy/types.yaml')['types']
    return {x['name']:x for x in items}

def load_relationships(root: Path):
    vals=load_yaml(root/'taxonomy/relationships.yaml')['relationships']
    return {x['name'] if isinstance(x,dict) else x for x in vals}

def load_statuses(root: Path): return load_yaml(root/'taxonomy/statuses.yaml')
def load_standard_categories(root: Path): return set(load_yaml(root/'taxonomy/standard-categories.yaml')['categories'])
