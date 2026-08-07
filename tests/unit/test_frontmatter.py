from scripts.lib.frontmatter import parse_frontmatter

def test_parse():
    fm,body=parse_frontmatter("---\nid: x\n---\n# Hi\n")
    assert fm["id"]=="x" and "Hi" in body
