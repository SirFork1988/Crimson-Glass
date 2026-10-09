#!/usr/bin/env python3
"""Build the native Plasma 6 Global Theme; never apply it to this desktop."""
# SPDX-License-Identifier: MIT
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'store/global-theme/org.crimsonglass.desktop'
ROUTES = {
    'plasma-style': 'plasma-themes.knsrc',
    'icons': 'icons.knsrc',
    'window-decoration': 'aurorae.knsrc',
    'wallpaper': 'wallpaper.knsrc',
    'cursors': 'xcursor.knsrc',
    'launcher': 'plasmoids.knsrc',
    'color-scheme': 'colorschemes.knsrc',
}
REQUIRED = set(ROUTES) - {'color-scheme'}


def dependency_uris(mapping):
    missing = sorted(REQUIRED - mapping.keys())
    if missing:
        raise ValueError('Missing published Store IDs: ' + ', '.join(missing))
    unknown = sorted(set(mapping) - ROUTES.keys())
    if unknown:
        raise ValueError('Unknown Store component keys: ' + ', '.join(unknown))
    result = []
    for component in ROUTES:
        if component not in mapping:
            continue
        value = mapping[component]
        if not isinstance(value, (str, int)) or isinstance(value, bool) or not re.fullmatch(r'[1-9][0-9]{3,9}', str(value)):
            raise ValueError(f'{component}: supply a real numeric published KDE Store content ID')
        result.append(f'kns://{ROUTES[component]}/api.kde-look.org/{value}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store-ids', type=Path, help='JSON object mapping documented component keys to published numeric Store IDs')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/store')
    parser.add_argument('--draft', action='store_true', help='Build a clearly named local test archive without download dependencies; do not upload it')
    args = parser.parse_args()
    metadata = json.loads((SOURCE / 'metadata.json').read_text())
    if args.draft:
        if args.store_ids:
            parser.error('--draft and --store-ids cannot be combined')
        metadata.pop('X-KPackage-Dependencies', None)
    else:
        if not args.store_ids:
            parser.error('Final Store archives require --store-ids; use --draft only for isolated local testing')
        try:
            metadata['X-KPackage-Dependencies'] = dependency_uris(json.loads(args.store_ids.read_text()))
        except (ValueError, OSError) as error:
            parser.error(str(error))
    suffix = '-DRAFT' if args.draft else ''
    filename = f"Crimson-Glass-Global-Theme-{metadata['KPlugin']['Version']}{suffix}.tar.gz"
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output / filename
    with output.open('wb') as file, gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as zipped:
        with tarfile.open(mode='w', fileobj=zipped, format=tarfile.PAX_FORMAT) as tar:
            for path in sorted(SOURCE.rglob('*')):
                if path.is_symlink() or not (path.is_file() or path.is_dir()):
                    raise ValueError(f'Unsupported file type in global theme: {path}')
                info = tar.gettarinfo(str(path), str(Path(SOURCE.name) / path.relative_to(SOURCE)))
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                info.mode = 0o755 if path.is_dir() else 0o644
                if path.is_dir():
                    tar.addfile(info)
                else:
                    data = (json.dumps(metadata, indent=2) + '\n').encode() if path.name == 'metadata.json' and path.parent == SOURCE else path.read_bytes()
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(f'{digest}  {output.name}\n')
    print(output)
    print(f'SHA256 {digest}')
    if args.draft:
        print('DRAFT: local package validation only; publish components and supply their IDs before upload.')


if __name__ == '__main__':
    main()
