"""Safe skill deployment: preview with --check, remove managed stale files with --prune."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
MANIFEST = '.modeling-display-manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reject_links(path):
    path = Path(os.path.abspath(path))
    for component in (path, *path.parents):
        if component.exists() or component.is_symlink():
            info = component.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise ValueError(f'Refusing link/reparse point: {component}')
    return path


def safe_file(root, rel):
    p = PurePosixPath(rel)
    if (not rel or '\\' in rel or ':' in rel or p.is_absolute()
            or any(x.lower() in ('..', '.git') for x in p.parts) or p.as_posix() != rel or not p.parts):
        raise ValueError(f'Unsafe manifest path: {rel!r}')
    path = reject_links(root.joinpath(*p.parts))
    if not path.resolve().is_relative_to(root.resolve()) or path == root:
        raise ValueError(f'Path leaves deployment root: {rel!r}')
    return path


def validate_root(root, repo):
    root = reject_links(root)
    source, dest = repo.resolve(), root.resolve()
    if dest.is_relative_to(source) or source.is_relative_to(dest):
        raise ValueError('Source and destination must not overlap')
    if root.exists() and not root.is_dir():
        raise ValueError('Destination is not a directory')
    if (root / '.git').exists() or (root / '.git').is_symlink():
        raise ValueError('Destination is a Git checkout; use a separate directory')
    return root


def collect(repo):
    """Copy current working-tree bytes for every Git-tracked project file."""
    repo = reject_links(repo).resolve()

    def git(*arguments):
        result = subprocess.run(['git', '-C', str(repo), *arguments], capture_output=True)
        if result.returncode:
            message = result.stderr.decode('utf-8', errors='replace').strip()
            raise ValueError(f'Cannot list Git project files: {message}')
        return result.stdout

    top = Path(os.fsdecode(git('rev-parse', '--show-toplevel')).strip()).resolve()
    if top != repo:
        raise ValueError('Deployment source must be the Git repository root')
    files = {}
    for entry in git('ls-files', '--stage', '--full-name', '-z').split(b'\0'):
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t', 1)
        mode, _, stage = metadata.split()
        rel = raw_path.decode('utf-8')
        if stage != b'0' or mode not in (b'100644', b'100755'):
            raise ValueError(f'Unmerged file, symbolic link or submodule cannot be deployed: {rel}')
        if rel == MANIFEST or rel.startswith('.modeling-display-backups/'):
            raise ValueError(f'Project file conflicts with deployment metadata: {rel}')
        path = safe_file(repo, rel)
        if not path.is_file():
            raise ValueError(f'Tracked file is missing: {rel}; restore it or stage its deletion with git add -u')
        files[rel] = path.read_bytes()
    if 'SKILL.md' not in files:
        raise ValueError('Git project must track SKILL.md')
    return files


def read_manifest(root):
    path = safe_file(root, MANIFEST)
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('schema') != 1 or not isinstance(value.get('files'), dict):
        raise ValueError('Invalid deployment manifest')
    for rel, sha in value['files'].items():
        safe_file(root, rel)
        if rel == MANIFEST or rel.startswith('.modeling-display-backups/'):
            raise ValueError('Manifest cannot manage its metadata/backups')
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
            raise ValueError('Invalid manifest checksum')
    return value['files']


def atomic_write(path, data):
    reject_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.deploy-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def plan_deployment(repo, root, files, prune=False):
    root = validate_root(root, repo)
    previous = read_manifest(root)
    writes, deletes = [], []
    for rel, data in files.items():
        path = safe_file(root, rel)
        if path.exists() and not path.is_file():
            raise ValueError(f'Expected file: {path}')
        if not path.exists() or path.read_bytes() != data:
            writes.append((rel, data))
    stale = {rel: sha for rel, sha in previous.items() if rel not in files}
    if prune:
        for rel, sha in stale.items():
            path = safe_file(root, rel)
            if path.exists():
                if not path.is_file() or digest(path.read_bytes()) != sha:
                    raise ValueError(f'Managed stale file was modified; preserve it manually: {rel}')
                deletes.append(rel)
        stale = {}
    managed = {**stale, **{rel: digest(data) for rel, data in files.items()}}
    manifest = (json.dumps({'schema': 1, 'files': managed}, ensure_ascii=False, indent=2) + '\n').encode()
    path = safe_file(root, MANIFEST)
    return root, writes, deletes, manifest, not path.exists() or path.read_bytes() != manifest


def apply_plan(plan):
    root, writes, deletes, manifest, manifest_changed = plan
    if not (writes or deletes or manifest_changed):
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup = safe_file(root, f'.modeling-display-backups/{stamp}')
    for rel in [r for r, _ in writes] + deletes + ([MANIFEST] if manifest_changed else []):
        source = safe_file(root, rel)
        if source.exists():
            destination = safe_file(backup, rel)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for rel, data in writes:
        atomic_write(safe_file(root, rel), data)
    for rel in deletes:
        safe_file(root, rel).unlink()
    if manifest_changed:
        atomic_write(safe_file(root, MANIFEST), manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('workbuddy', 'codex', 'codex-prompt'))
    parser.add_argument('--check', action='store_true', help='Read-only preview; exit 1 if differences exist')
    parser.add_argument('--prune', action='store_true', help='Remove unchanged stale files in previous manifest')
    parser.add_argument('--home', type=Path, default=Path.home(), help='Home override for isolated installs')
    args = parser.parse_args(argv)
    try:
        home = reject_links(args.home)
        targets = {'workbuddy': home / '.workbuddy/skills/modeling-display',
                   'codex': home / '.codex/skills/modeling-display'}
        files = collect(REPO)
        plans = [(name, plan_deployment(REPO, root, files, args.prune))
                 for name, root in targets.items() if args.target in (None, name)]
        prompt, prompt_changed = None, False
        if args.target in (None, 'codex', 'codex-prompt'):
            prompt = reject_links(home / '.codex/prompts/geo3d.md')
            if prompt.resolve().is_relative_to(REPO.resolve()):
                raise ValueError('Prompt destination overlaps source')
            data = reject_links(REPO / 'prompts/geo3d.md').read_bytes()
            if prompt.exists() and not prompt.is_file():
                raise ValueError('Prompt destination is not a file')
            prompt_changed = not prompt.exists() or prompt.read_bytes() != data
        changed = any(p[1] or p[2] or p[4] for _, p in plans) or prompt_changed
        # Preflight every target before the first write.
        for name, plan in plans:
            print(f'[{name}] update={len(plan[1])}, prune={len(plan[2])}, manifest={plan[4]} -> {plan[0]}')
            if not args.check:
                apply_plan(plan)
        if prompt_changed:
            print(f'[codex-prompt] update -> {prompt}')
            if not args.check:
                if prompt.exists():
                    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
                    backup = reject_links(prompt.parent / '.modeling-display-backups' / stamp / prompt.name)
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(prompt, backup)
                atomic_write(prompt, data)
        return 1 if args.check and changed else 0
    except (ValueError, OSError) as error:
        print(f'Deployment failed: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
