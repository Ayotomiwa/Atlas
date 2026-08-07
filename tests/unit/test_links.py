from pathlib import Path
from scripts.lib.links import unresolved_links
def test_links(tmp_path):
    (tmp_path/'b.md').write_text('ok'); p=tmp_path/'a.md'; p.write_text('[b](b.md)\n[bad](missing.md)')
    assert unresolved_links(p,tmp_path)==['missing.md']
