from pathlib import Path
from scripts.atlas_lint import lint
def test_repository_lint_has_no_errors():
    root=Path(__file__).resolve().parents[2]; issues=lint(root); assert [i for i in issues if i['level']=='ERROR']==[]
def test_no_staging_bucket_indexes():
    root=Path(__file__).resolve().parents[2]
    for p in (root/'_staging').iterdir():
        if p.is_dir(): assert not (p/'index.md').exists()
def test_contract_counts():
    root=Path(__file__).resolve().parents[2]
    curated=['components','flows','infra','schema-info','business-concepts','standards','runbooks','incidents']
    assert all(all((root/'_curated'/c/f).exists() for f in ['README.md','index.md','_template.md']) for c in curated)
    staging=['changes','components','flows','infra','schema-info','business-concepts','incidents','runbooks','standards']
    assert all(all((root/'_staging'/c/f).exists() for f in ['README.md','_template.md']) for c in staging)
