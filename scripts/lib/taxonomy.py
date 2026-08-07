from pathlib import Path
import yaml

def load_yaml(path):
    with Path(path).open(encoding='utf-8') as f: return yaml.safe_load(f)
def load_taxonomy(root):
    root=Path(root)
    return {
      'types': load_yaml(root/'taxonomy/types.yaml'),
      'relationships': load_yaml(root/'taxonomy/relationships.yaml'),
      'statuses': load_yaml(root/'taxonomy/statuses.yaml'),
      'categories': load_yaml(root/'taxonomy/standard-categories.yaml')}
