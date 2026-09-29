# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
"""Explicit source/media policy. No runtime secrets or recursively copied data."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT))
from safeio import checked_path
from install import APP_FILES, DOC_FILES

ASSETS = {
    'docs/images/setup-tab-0.png': '14effe239e2f1e99b448f99e6588c0025775a2e389e2d80e67793abc687dcd76',
    'docs/images/setup-tab-1.png': '90cec8fa3dfc984044d941cd4dcdbc0d005f815fd3d776506aa10c615748de53',
    'docs/images/setup-tab-2.png': '684fa8ffd27e5286c6dd82e7b082108c136d0dd28758354f9b993f350b0c7d0c',
    'docs/images/setup-tab-3.png': '0d8aad5d491573fd1d869fb8ac6e2f5ad4c79958b5e1e8415e9d149c8979769c',
    'docs/images/cases/case-natural-one-line-request.png': 'fae17c536b1fb476a90f61d41a00924d02ecf323c9e963554319a76f0e52aada',
    'docs/images/cases/case-natural-one-line.png': '09247e5bd6214038b1055d0408600f236f5f3f35fd04c95bebdecd04a14e32e1',
    'docs/images/cases/case-shibuya-crossing-detailed.png': '028feb40e09f214e0d43925fdc8c587efb3cd393aed8f01a1840dd10def17ae8',
    'docs/images/cases/case-showa-house-detailed.png': '837e15d4879eec21dd178415851602c406e0a7b491a735d32342cab6ee40a8b2',
    'app/resources/Bridge.icns': '847609aa8e62a3e6260a262eab54da3909e27e0d88a732878abc7d68b3061e9c',
}
TEXT_FILES = tuple('app/' + name for name in APP_FILES) + tuple('docs/' + name for name in DOC_FILES) + (
    'install.py', 'Install.command', 'LICENSE', 'README_RC2.md', 'dependencies.lock.json', 'requirements.lock',
    'tools/release_policy.py', 'tools/build_public.py')
FORBIDDEN = (
    ('api_key_value', re.compile(r'\bsk-(?:(?:proj|svcacct)-)?[A-Za-z0-9_-]{24,}')),
    ('github_token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{40,})')),
    ('tunnel_identity', re.compile(r'\btunnel_[A-Za-z0-9_-]{16,128}\b')),
    ('personal_home', re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/')),
    ('private_repo', re.compile(r'nas-backup/|HANDOFF_CHATGPT_WEB|codex/[A-Za-z0-9_-]*handoff')),
    ('email_address', re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')),
    ('private_key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
)


def scan_text(text):
    # Scanner pattern declarations are not private data. They remain literal
    # detectors; skip nothing in other files. The policy module is scanned by the
    # caller except for these declared detector source lines.
    return [name for name, expression in FORBIDDEN if expression.search(text)]


def file_bytes(root, name):
    path = checked_path(root / name)
    if not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('Missing or unsafe release file: ' + name)
    return path.read_bytes()


def verify(root=ROOT, require_media=True):
    failures, selected = [], {}
    for name in TEXT_FILES:
        try:
            raw = file_bytes(root, name)
            text = raw.decode('utf-8', 'strict')
            # Only the literal detector definitions in this one fixed module are
            # excluded from self-matching. All actual content is still checked.
            if name == 'tools/release_policy.py':
                start = text.index('FORBIDDEN = (')
                end = text.index('\n)\n', start) + 3
                text = text[:start] + text[end:]
            findings = scan_text(text)
            failures += [name + ': ' + finding for finding in findings]
            selected[name] = raw
        except (OSError, ValueError, UnicodeError) as exc:
            failures.append(name + ': ' + type(exc).__name__)
    if not require_media:
        return failures, selected
    try:
        manifest = json.loads(file_bytes(root, 'release-assets.json'))
        records = manifest['assets']
        if not isinstance(records, list) or len(records) != len(ASSETS):
            raise ValueError('Invalid media manifest')
        mapped = {record['path']: record for record in records}
        if set(mapped) != set(ASSETS) or len(mapped) != len(records):
            raise ValueError('Unexpected media paths')
    except (OSError, ValueError, TypeError, KeyError):
        failures.append('release-assets.json: invalid_manifest')
        return failures, selected
    import datetime
    reviewed = []
    for name, digest in ASSETS.items():
        record = mapped[name]
        try:
            raw = file_bytes(root, name)
            if hashlib.sha256(raw).hexdigest() != digest or record.get('sha256') != digest:
                raise ValueError('hash_mismatch')
            if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff') or
                    (name.endswith('.icns') and raw.startswith(b'icns'))):
                raise ValueError('unsupported_media_magic')
            if any(record.get(key) is not True for key in ('human_reviewed', 'metadata_reviewed', 'approved_for_public')):
                raise ValueError('human_review_missing')
            reference = record.get('review_reference')
            if not isinstance(reference, str) or not reference.strip() or scan_text(reference):
                raise ValueError('invalid_review_reference')
            stamp = datetime.datetime.fromisoformat(str(record['reviewed_at']).replace('Z', '+00:00'))
            if stamp.tzinfo is None or stamp > datetime.datetime.now(datetime.timezone.utc):
                raise ValueError('invalid_review_date')
            selected[name] = raw
            reviewed.append({'path': name, 'sha256': digest, 'human_reviewed': True,
                             'metadata_reviewed': True, 'approved_for_public': True,
                             'reviewed_at': stamp.isoformat()})
        except (OSError, ValueError, TypeError, KeyError) as exc:
            # No arbitrary exception text / local absolute path is exported.
            failures.append(name + ': unavailable_or_unapproved_' + type(exc).__name__)
    selected['RELEASE_IMAGE_REVIEW.json'] = (json.dumps({'schema': 1, 'assets': reviewed}, indent=2) + '\n').encode()
    public_records = [dict(entry, review_reference='sha256:' + hashlib.sha256(mapped[entry['path']]['review_reference'].encode()).hexdigest()) for entry in reviewed]
    selected['release-assets.json'] = (json.dumps({'schema': 1, 'assets': public_records}, indent=2) + '\n').encode()
    return failures, selected
