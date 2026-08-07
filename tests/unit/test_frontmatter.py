import pytest
from scripts.lib.frontmatter import parse_frontmatter_text
def test_parse_frontmatter():
    fm,body=parse_frontmatter_text('---\nid: x\n---\nhello\n'); assert fm['id']=='x' and 'hello' in body
def test_bad_frontmatter():
    with pytest.raises(ValueError): parse_frontmatter_text('---\nid: x\n')
