"""Scan tracked files/history without ever displaying secret values."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [re.compile(rb'AIza[0-9A-Za-z_-]{30,}'), re.compile(rb'AQ\.[0-9A-Za-z_-]{35,}'),
            re.compile(rb'gh[pousr]_[0-9A-Za-z]{30,}'), re.compile(rb'sk-[0-9A-Za-z_-]{24,}'),
            re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True)

def suspicious(data):
    return any(p.search(data) for p in PATTERNS)

def main():
    findings = set()
    tracked = git('ls-files', '-z')
    if tracked.returncode == 0:
        files = [ROOT / p.decode() for p in tracked.stdout.split(b'\0') if p]
    else:
        excluded = {'.git', '.venv', '.venv-clean', '__pycache__', '.pytest_cache', 'chroma_db', 'node_modules'}
        files = [p for p in ROOT.rglob('*') if p.is_file() and not set(p.relative_to(ROOT).parts) & excluded
                 and p.name != '.env' and p.suffix != '.pdf']
    # Also check untracked source/docs/logs, excluding intentionally local secret files.
    for base in ['src', 'scripts', 'tests', 'docs', 'logs']:
        files.extend(p for p in (ROOT / base).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files.extend([ROOT / '.env.example', ROOT / 'README.md'])
    for p in set(files):
        if p.is_file() and suspicious(p.read_bytes()):
            findings.add(('working-tree', str(p.relative_to(ROOT))))
    commits = git('rev-list', '--all', '--reflog')
    commit_ids = set(commits.stdout.decode().split()) if commits.returncode == 0 else set()
    for commit in commit_ids:
        if suspicious(git('cat-file', 'commit', commit).stdout):
            findings.add((commit, '(commit metadata/message)'))
        tree = git('ls-tree', '-r', '-z', commit).stdout
        for record in tree.split(b'\0'):
            if not record: continue
            info, name = record.split(b'\t', 1)
            oid = info.split()[2].decode()
            if suspicious(git('cat-file', 'blob', oid).stdout):
                findings.add((commit, name.decode()))
    for commit, name in sorted(findings):
        print(f'FAIL file={name} commit={commit}')
    print(f'Secret scan: {"FAIL" if findings else "PASS"}; {len(set(files))} working files, {len(commit_ids)} commits scanned; values never displayed.')
    if not commit_ids: print('History: no commits exist yet.')
    return 1 if findings else 0

if __name__ == '__main__':
    raise SystemExit(main())
