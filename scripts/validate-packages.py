#!/usr/bin/env python3
"""Validate the package identity that Click checks before installation."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile


def validate(root):
    seen = set()
    for path in sorted((root / 'manifests').glob('*.json')):
        manifest = json.loads(path.read_text())
        for key in ('id', 'name', 'version', 'packageUrl', 'sha256', 'manifestUrl'):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                raise ValueError(f'{path}: missing {key}')
        plugin_id = manifest['id']
        if not re.fullmatch(r'[a-z0-9-]+', plugin_id) or plugin_id in seen:
            raise ValueError(f'{path}: invalid or duplicate ID')
        seen.add(plugin_id)
        if path.stem != plugin_id or manifest['manifestUrl'].split('/')[-1] != path.name:
            raise ValueError(f'{path}: manifest URL/filename must match its ID')
        package = root / 'packages' / manifest['packageUrl'].split('/')[-1]
        if hashlib.sha256(package.read_bytes()).hexdigest() != manifest['sha256']:
            raise ValueError(f'{path}: package checksum mismatch')
        with zipfile.ZipFile(package) as archive:
            names = archive.namelist()
            if any(n.startswith('/') or '..' in PurePosixPath(n).parts or '\\' in n for n in names):
                raise ValueError(f'{path}: unsafe archive path')
            metadata = [n for n in names if PurePosixPath(n).name == 'plugin.json']
            if len(metadata) != 1:
                raise ValueError(f'{path}: expected one plugin.json')
            info = json.loads(archive.read(metadata[0]))
            generated = re.sub('-+', '-', re.sub('[^a-z0-9]', '-', info['name'], flags=re.I)).lower().strip('-')
            if generated != plugin_id:
                raise ValueError(f'{path}: package ID {generated} differs from manifest ID {plugin_id}')
            if info['version'] != manifest['version'] or info['name'] != manifest['name']:
                raise ValueError(f'{path}: package name/version differs from manifest')
            bootstrap = str(PurePosixPath(metadata[0]).parent / 'bootstrap.php')
            if bootstrap not in names:
                raise ValueError(f'{path}: missing bootstrap.php')
    if not seen:
        raise ValueError('No plugin manifests found')
    return len(seen)


if __name__ == '__main__':
    try:
        print(f'Validated {validate(Path(sys.argv[1] if len(sys.argv) > 1 else "."))} plugin packages.')
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit(str(error))
