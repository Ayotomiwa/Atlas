from scripts.lib.links import broken_links

def test_links(tmp_path):
    (tmp_path/"ok.md").write_text("ok")
    p=tmp_path/"a.md"; p.write_text("[ok](ok.md)")
    assert broken_links(p)==[]
