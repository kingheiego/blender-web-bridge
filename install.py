#!/usr/bin/env python3
# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
"""Transactional per-user installer. No service stop, networking or Blender calls.

Each target has its own staging/backup directory on the target filesystem.
Commit is journaled, not globally atomic across volumes. Only transaction-owned
inodes may be quarantined/restored. A failed rollback blocks subsequent updates.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import os
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'app'))
from safeio import FileLock, atomic_bytes, atomic_json, checked_path, identity, private_dir, rename_owned, fsync_dir

MIN_PYTHON = (3, 10)
RECOMMENDED_PYTHON = (3, 11)
VERSION = '2.0.2-rc3'
BUNDLE_SHORT_VERSION = '2.0.2'
BUNDLE_BUILD = '20205'
APP_NAME = 'Blender Web Bridge'
APP_DISPLAY_NAME = 'Blender Web Bridge / Blender 網頁橋接器'
DEFAULT_TUNNEL_LABEL = 'org.blenderwebbridge.tunnel'
LABEL_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,199}')
APP_FILES = ('desktop.py', 'bridge.py', 'health.py', 'safeio.py', 'settings.py',
             'bootstrap.py', 'keychain_store.py', 'mcp_entry.py', 'workflow.py',
             'enable_addon.py')
DOC_FILES = ('README_RC2.zh-Hant.md', 'SETUP_RC2.html', 'TROUBLESHOOTING_RC2.md',
             'EXAMPLES_RC2.md', 'SECURITY_RC2.md', 'ACCEPTANCE.md', 'NETWORK_RECOVERY.md')
ASSET_FILES = tuple('docs/images/setup-tab-%d.png' % i for i in range(4)) + (
    'docs/images/cases/case-natural-one-line-request.png',
    'docs/images/cases/case-natural-one-line.png',
    'docs/images/cases/case-shibuya-crossing-detailed.png',
    'docs/images/cases/case-showa-house-detailed.png', 'app/resources/Bridge.icns')


class ConfigError(RuntimeError):
    pass


class ServiceStateUnknown(RuntimeError):
    pass


class PrerequisiteError(RuntimeError):
    pass


def check_python(version_info=None, import_tk=None):
    version = tuple(version_info or sys.version_info)
    if version[:2] < MIN_PYTHON:
        return False, 'Python 3.10+ with Tk required; 3.11+ recommended / 需要 Python 3.10+ 及 Tk'
    try:
        if import_tk:
            import_tk()
        else:
            __import__('tkinter')
    except Exception:
        return False, 'Tk unavailable / 未能載入 Tk'
    return True, 'ok'


def read_config(data):
    path = checked_path(Path(data) / 'config.json')
    if not path.exists():
        return {}, DEFAULT_TUNNEL_LABEL
    try:
        config = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ConfigError('Existing config cannot be read / 未能讀取現有設定') from exc
    if not isinstance(config, dict):
        raise ConfigError('Config must be an object / 設定必須是物件')
    label = config.get('tunnel_label', DEFAULT_TUNNEL_LABEL)
    blender_label = config.get('blender_label', 'org.blenderwebbridge.blender')
    if not isinstance(label, str) or not LABEL_RE.fullmatch(label):
        raise ConfigError('Invalid tunnel_label / 通道服務名稱無效')
    if not isinstance(blender_label, str) or not LABEL_RE.fullmatch(blender_label) or label == blender_label:
        raise ConfigError('Service names must be valid and distinct / 服務名稱必須有效且不同')
    for key in ('state_root', 'runtime_root'):
        if key in config and (not isinstance(config[key], str) or not Path(config[key]).expanduser().is_absolute()):
            raise ConfigError('Configured storage paths must be absolute / 設定路徑必須是絕對路徑')
    return config, label


def _run(args, timeout=8):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def service_state(label, runner=_run):
    if not isinstance(label, str) or not LABEL_RE.fullmatch(label):
        raise ConfigError('Invalid service name / 服務名稱無效')
    try:
        response = runner(['launchctl', 'print', f'gui/{os.getuid()}/{label}'])
    except (OSError, subprocess.SubprocessError) as exc:
        raise ServiceStateUnknown('Cannot verify tunnel service / 未能確認通道服務狀態') from exc
    if response.returncode == 0:
        return 'loaded'
    output = (response.stderr or '') + (response.stdout or '')
    # launchctl's missing-service error must identify the service, not just contain
    # a generic "not found" which could be a missing domain or executable.
    if 'Could not find service' in output and re.search(r'(?<![A-Za-z0-9._-])' + re.escape(label) + r'(?![A-Za-z0-9._-])', output):
        return 'unloaded'
    raise ServiceStateUnknown('Ambiguous launchctl response / launchctl 回覆不明確')


InstallLock = FileLock


def _copy(source, target):
    source = checked_path(source)
    if not source.is_file() or source.stat().st_nlink != 1:
        raise ValueError('Source must be a regular unlinked file / 來源檔案不安全')
    private_dir(target.parent)
    shutil.copy2(source, target, follow_symlinks=False)


def _payload(source, destination):
    private_dir(destination)
    for name in APP_FILES:
        _copy(source / 'app' / name, destination / name)
    for name in ('dependencies.lock.json', 'requirements.lock', 'README_RC2.md', 'LICENSE', 'release-assets.json'):
        _copy(source / name, destination / name)
    for name in DOC_FILES:
        _copy(source / 'docs' / name, destination / 'docs' / name)
    # No recursive docs copy: private handoff notes, logs and accounts are not assets.
    for name in ASSET_FILES:
        item = checked_path(source / name)
        if item.is_file():
            relative = Path(name).relative_to('app') if name.startswith('app/') else Path(name)
            _copy(item, destination / relative)


def _sync_tree(path):
    """Flush staged file data and directory entries before recording commit intent."""
    entries = list(path.rglob('*')) if path.is_dir() else [path]
    for item in entries:
        checked_path(item)
        if item.is_file():
            with item.open('rb') as stream:
                os.fsync(stream.fileno())
    for directory in sorted((p for p in entries if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        fsync_dir(directory)
    fsync_dir(path if path.is_dir() else path.parent)


def _tree_hash(path):
    records = {}
    for item in sorted(path.rglob('*')):
        checked_path(item)
        if item.is_file():
            records[item.relative_to(path).as_posix()] = hashlib.sha256(item.read_bytes()).hexdigest()
        elif not item.is_dir():
            raise ValueError('Special source file refused')
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def build_bundle(source, target, final_data, python=None, version=BUNDLE_SHORT_VERSION, build=BUNDLE_BUILD):
    if not re.fullmatch(r'\d+(?:\.\d+){0,2}', version) or not re.fullmatch(r'\d+', build):
        raise ValueError('Bundle version and build must be numeric')
    contents = private_dir(target / 'Contents')
    executable = private_dir(contents / 'MacOS') / 'BlenderWebBridge'
    resources = private_dir(contents / 'Resources')
    args = shlex.join([python or sys.executable, str(final_data / 'app' / 'desktop.py')])
    script = '#!/bin/sh\nexport BLENDER_WEB_BRIDGE_DATA=' + shlex.quote(str(final_data)) + '\nexec ' + args + ' "$@"\n'
    atomic_bytes(executable, script.encode(), 0o755)
    info = {'CFBundleName': APP_NAME, 'CFBundleDisplayName': APP_DISPLAY_NAME,
            'CFBundleIdentifier': 'org.blenderwebbridge.app', 'CFBundleExecutable': 'BlenderWebBridge',
            'CFBundlePackageType': 'APPL', 'CFBundleShortVersionString': version,
            'CFBundleVersion': build, 'NSHighResolutionCapable': True}
    icon = checked_path(source / 'app/resources/Bridge.icns')
    if icon.is_file():
        _copy(icon, resources / 'Bridge.icns')
        info['CFBundleIconFile'] = 'Bridge.icns'
    atomic_bytes(contents / 'Info.plist', plistlib.dumps(info))


def _overlap(a, b):
    return a == b or a in b.parents or b in a.parents


def _validate_roots(source, data, desktop, state):
    for path in (source, data, desktop, state):
        checked_path(path)
    for a, b in ((source, data), (source, desktop), (data, desktop)):
        if _overlap(a, b):
            raise ValueError('Source/data/Desktop roots overlap / 來源及安裝路徑重疊')
    for target in (data / 'app', desktop / (APP_NAME + '.app')):
        if _overlap(state, target):
            raise ValueError('State cannot overlap a replaced target / 狀態資料夾與更新目標重疊')
        checked_path(target)


def _target_record(target, transaction_id):
    private_dir(target.parent)
    stage = Path(tempfile.mkdtemp(prefix='.bwb-' + transaction_id + '-', dir=target.parent))
    return {'target': str(target), 'stage': str(stage), 'new': str(stage / 'new'),
            'previous': str(stage / 'previous'), 'quarantine': str(stage / 'rollback-new'),
            'old_identity': identity(target), 'new_identity': None}


def _checkpoint(journal_path, journal, phase):
    journal['phase'] = phase
    atomic_json(journal_path, journal)


def _validate_journal(journal, data, desktop, state):
    if not isinstance(journal, dict) or journal.get('schema') != 2:
        raise ValueError('Invalid transaction journal')
    txid = journal.get('transaction_id', '')
    if not isinstance(txid, str) or not re.fullmatch('[0-9a-f]{32}', txid):
        raise ValueError('Invalid transaction ID')
    expected = [data / 'app', desktop / (APP_NAME + '.app'), state / 'installation.json']
    records = journal.get('targets')
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError('Invalid transaction targets')
    for record, target in zip(records, expected):
        if not isinstance(record, dict) or Path(record['target']) != target:
            raise ValueError('Unexpected recovery target')
        stage = checked_path(record['stage'])
        if stage.parent != target.parent or not stage.name.startswith('.bwb-' + txid + '-'):
            raise ValueError('Unexpected staging directory')
        for key, suffix in (('new', 'new'), ('previous', 'previous'), ('quarantine', 'rollback-new')):
            if Path(record[key]) != stage / suffix:
                raise ValueError('Unexpected backup path')
        checked_path(target)


def _rollback(journal, path):
    failures = []
    for record in reversed(journal['targets']):
        target, previous = Path(record['target']), Path(record['previous'])
        try:
            current = identity(target)
            old, new = record['old_identity'], record['new_identity']
            if current is not None and new is not None and current == new:
                rename_owned(target, Path(record['quarantine']), new)
                current = None
            if current is not None and current != old:
                raise ValueError('Target is not transaction-owned; manual recovery required')
            if old is not None:
                backup = identity(previous)
                if current == old and backup is None:
                    continue
                if current is None and backup == old:
                    rename_owned(previous, target, old)
                else:
                    raise ValueError('Previous target could not be proven/restored')
            elif current is not None:
                raise ValueError('Unexpected target during first-install rollback')
        except Exception as exc:
            failures.append({'target_index': journal['targets'].index(record), 'error_type': type(exc).__name__})
    journal['rollback_failures'] = failures
    try:
        _checkpoint(path, journal, 'rollback_incomplete' if failures else 'rolled_back')
    except Exception as exc:
        failures.append({'target_index': -1, 'error_type': type(exc).__name__})
    return failures


def install(source, data, desktop, *, version=VERSION, bundle_version=BUNDLE_SHORT_VERSION,
            build=BUNDLE_BUILD, service_runner=_run, lock_path=None, rollback=False):
    journal = None
    stages = []
    mutated = False
    stack = contextlib.ExitStack()
    try:
        source, data, desktop = map(checked_path, (source, data, desktop))
        config, label = read_config(data)
        state = checked_path(config.get('state_root', data / 'state'))
        _validate_roots(source, data, desktop, state)
        private_dir(state)
        # Same lock names/inodes as controller, CLI and exec'ed tunnel daemon.
        for filename in ('ui.lock', 'control.lock', 'daemon.lock'):
            stack.enter_context(FileLock(lock_path if filename == 'ui.lock' and lock_path else state / filename))
        current_config, current_label = read_config(data)
        if current_config != config or current_label != label:
            raise ConfigError('Configuration changed while acquiring locks')
        if service_state(label, service_runner) != 'unloaded':
            return {'ok': False, 'message': 'Stop the tunnel and quit the panel first / 請先停止通道並關閉面板；Blender 可保持開啟'}
        journal_path = state / 'install-transaction.json'
        checked_path(journal_path)
        previous_journal = json.loads(journal_path.read_text()) if journal_path.exists() else None
        if previous_journal:
            _validate_journal(previous_journal, data, desktop, state)
            if rollback:
                failures = _rollback(previous_journal, journal_path)
                return {'ok': not failures, 'rollback_incomplete': bool(failures),
                        'message': 'Rollback incomplete / 還原未完成' if failures else 'Rollback completed / 已還原'}
            if previous_journal.get('phase') not in ('committed', 'rolled_back'):
                return {'ok': False, 'rollback_incomplete': True,
                        'message': 'Unfinished installation; explicit --rollback required / 上次安裝未完成，需明確執行 --rollback'}
        elif rollback:
            return {'ok': False, 'message': 'No transaction to roll back / 沒有可還原交易'}
        # Preserve last completed journal before starting a new transaction.
        if previous_journal:
            atomic_json(state / 'install-history' / (previous_journal['transaction_id'] + '.json'), previous_journal)
        txid = uuid.uuid4().hex
        targets = []
        for target in (data / 'app', desktop / (APP_NAME + '.app'), state / 'installation.json'):
            record = _target_record(target, txid)
            stages.append(Path(record['stage']))
            targets.append(record)
        journal = {'schema': 2, 'transaction_id': txid, 'targets': targets,
                   'phase': 'staging', 'version': version, 'build': build}
        _payload(source, Path(targets[0]['new']))
        build_bundle(source, Path(targets[1]['new']), data, version=bundle_version, build=build)
        _sync_tree(Path(targets[0]['new']))
        _sync_tree(Path(targets[1]['new']))
        receipt = {'schema': 2, 'transaction_id': txid, 'version': version,
                   'bundle_version': bundle_version, 'build': build,
                   'installed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'payload_sha256': _tree_hash(Path(targets[0]['new'])),
                   'bundle_sha256': _tree_hash(Path(targets[1]['new'])),
                   'source': str(source), 'data': str(data), 'desktop': str(desktop),
                   'tunnel_label': label}
        atomic_json(Path(targets[2]['new']), receipt)
        for record in targets:
            record['new_identity'] = identity(Path(record['new']))
        # Durable intent exists before the first rename; crash recovery uses
        # inode identities even if the subsequent checkpoint never completed.
        _checkpoint(journal_path, journal, 'prepared')
        for index, record in enumerate(targets):
            target, new, previous = (Path(record[key]) for key in ('target', 'new', 'previous'))
            _checkpoint(journal_path, journal, 'swapping_' + str(index))
            if record['old_identity'] is not None:
                mutated = True
                rename_owned(target, previous, record['old_identity'])
            mutated = True
            rename_owned(new, target, record['new_identity'])
        _checkpoint(journal_path, journal, 'committed')
        return {'ok': True, 'message': 'Installed; nothing was started / 安裝完成，未啟動任何服務',
                'receipt': str(state / 'installation.json'), 'transaction_id': txid}
    except Exception as exc:
        failures = []
        if mutated and journal is not None:
            try:
                # Locks remain held through rollback and the terminal journal write.
                failures = _rollback(journal, state / 'install-transaction.json')
            except Exception as recovery_error:
                failures.append({'target_index': -1, 'error_type': type(recovery_error).__name__})
        elif journal is not None:
            # Prepared-but-not-mutated journals still need a terminal state.
            try:
                if (state / 'install-transaction.json').exists():
                    persisted = json.loads((state / 'install-transaction.json').read_text())
                    if persisted.get('transaction_id') == journal['transaction_id']:
                        _checkpoint(state / 'install-transaction.json', journal, 'rolled_back')
            except Exception:
                failures.append({'target_index': -1, 'error_type': 'JournalWriteError'})
        return {'ok': False, 'error_type': type(exc).__name__, 'rollback_incomplete': bool(failures),
                'message': ('Installation failed; manual recovery required / 安裝失敗，需人工還原' if failures else
                            'Installation refused or rolled back / 安裝已拒絕或還原'),
                'reason': str(exc) if isinstance(exc, (ConfigError, ServiceStateUnknown, ValueError, BlockingIOError)) else type(exc).__name__}
    finally:
        # Never delete a stage that may hold the sole remaining copy of prior data.
        try:
            if not mutated:
                for stage in stages:
                    if stage.exists() and not (stage / 'previous').exists():
                        with contextlib.suppress(OSError):
                            shutil.rmtree(stage)
        finally:
            stack.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--data', type=Path, default=Path(os.environ.get('BLENDER_WEB_BRIDGE_DATA', str(Path.home() / 'Library/Application Support/BlenderWebBridge'))))
    parser.add_argument('--desktop', type=Path, default=Path.home() / 'Desktop')
    parser.add_argument('--check', action='store_true', help='Check Python/Tk only; write nothing')
    parser.add_argument('--rollback', action='store_true', help='Explicitly restore the latest transaction; tunnel must be stopped')
    options = parser.parse_args(argv)
    ok, message = check_python()
    if not ok:
        print(message, file=sys.stderr)
        return 1
    if options.check:
        print('Python/Tk prerequisite passed; no installation performed / Python/Tk 檢查通過，未安裝')
        return 0
    if sys.platform != 'darwin':
        print('Installation is macOS-only. Tests run on other systems / 安裝只支援 macOS', file=sys.stderr)
        return 1
    outcome = install(options.source, options.data, options.desktop, rollback=options.rollback)
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0 if outcome['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
