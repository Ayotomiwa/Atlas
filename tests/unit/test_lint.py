import subprocess, sys

def test_repo_lint_clean():
    p=subprocess.run([sys.executable,"scripts/atlas_lint.py","."],capture_output=True,text=True)
    assert p.returncode==0, p.stdout+p.stderr
