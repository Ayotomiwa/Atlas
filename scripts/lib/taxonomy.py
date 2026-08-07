from pathlib import Path
import yaml

def load_yaml(root, rel):
    return yaml.safe_load((Path(root)/rel).read_text(encoding='utf-8'))

def type_map(root):
    return {x['name']:x for x in load_yaml(root,'taxonomy/types.yaml')['types']}

def relationship_names(root):
    return {x['name'] for x in load_yaml(root,'taxonomy/relationships.yaml')['relationships']}

def status_sets(root):
    y=load_yaml(root,'taxonomy/statuses.yaml')
    return ({x['name'] for x in y['curated_status']},{x['name'] for x in y['staging_status']},set(y['relationship_confidence']))
