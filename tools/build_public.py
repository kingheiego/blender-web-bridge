#!/usr/bin/env python3
"""Build an allowlisted public source ZIP only after all privacy/media gates pass."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

from release_policy import ROOT, verify
from safeio import checked_path, fsync_dir


def build(root, output):
    failures, selected = verify(root, require_media=True)
    if failures:
        return {'ok': False, 'errors': failures, 'output_created': False}
    output = checked_path(output)
    if output.exists():
        raise FileExistsError('Output exists; refusing overwrite')
    if not output.parent.is_dir():
        raise ValueError('Output directory must already exist')
    # Keep the source name so installer input and any patch remain consistent.
    selected['README.md'] = selected['README_RC2.md']
    manifest = {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(selected.items())}
    selected['PUBLIC_SOURCE_SHA256.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    fd, temporary_name = tempfile.mkstemp(prefix='.bwb-public-', dir=output.parent)
    temporary = Path(temporary_name)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, raw in sorted(selected.items()):
                info = zipfile.ZipInfo('blender-web-bridge/' + name, (2026, 9, 29, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (0o100755 if name == 'Install.command' else 0o100644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, raw)
        with temporary.open('rb') as stream:
            os.fsync(stream.fileno())
        # Atomic no-clobber publication on the same filesystem, not a remote push.
        os.link(temporary, output, follow_symlinks=False)
        fsync_dir(output.parent)
    finally:
        temporary.unlink(missing_ok=True)
    return {'ok': True, 'output_created': True, 'files': len(selected),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    if args.check:
        errors, _ = verify(args.root, require_media=True)
        result = {'ok': not errors, 'errors': errors, 'output_created': False}
    elif args.output:
        try:
            result = build(args.root, args.output)
        except (OSError, ValueError) as exc:
            result = {'ok': False, 'error_type': type(exc).__name__, 'output_created': False}
    else:
        parser.error('Use --check or --output')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
