#!/usr/bin/env python3
"""One launchd supervisor; observational health; never replay model operations."""
from __future__ import annotations

import concurrent.futures
import json
import math
import os
import pathlib
import plistlib
import re
import socket
import subprocess
import sys
import time
import threading
import uuid

from settings import ROOT, CONFIG, STATE, RUNTIME, CONFIG_PATH, DATA, validate
from keychain_store import load_credential
from bootstrap import write_profile
from safeio import FileLock, atomic_bytes, atomic_json, checked_path, private_dir
from health import (OBSERVER, FRESH_WINDOW_SECONDS, MAX_METRICS_BYTES, inspect_cloud,
                    local_get, local_url, result as cloud_result)

LABEL = CONFIG['tunnel_label']
DOMAIN = f'gui/{os.getuid()}'
PLIST = pathlib.Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')
HEALTH = STATE / 'health-url.txt'
LOG = STATE / 'tunnel.log'
PYTHON = sys.executable
WEB_TTL_SECONDS = 300
# Acceptance is deliberately limited to this observing controller session.
# A panel restart cannot resurrect a pass after an unobserved outage.
_WEB_SESSION = uuid.uuid4().hex
_WEB_REVOKED = set()
_WEB_LOCK = threading.Lock()


def invalidate_web_acceptance():
    """Locally revoke the current attestation after observation failure, no RPC."""
    try:
        raw = checked_path(STATE / 'web-acceptance.json').read_bytes()
        import hashlib
        with _WEB_LOCK:
            _WEB_REVOKED.add(hashlib.sha256(raw).hexdigest())
    except (OSError, ValueError):
        return


def command(args, timeout=8):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def service(label):
    if not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,199}', label):
        return {'known': False, 'loaded': None, 'pid': None, 'state': 'unknown'}
    try:
        response = command(['launchctl', 'print', f'{DOMAIN}/{label}'])
    except (OSError, subprocess.SubprocessError):
        return {'known': False, 'loaded': None, 'pid': None, 'state': 'unknown'}
    if response.returncode:
        text = (response.stderr or '') + (response.stdout or '')
        missing = 'Could not find service' in text and bool(re.search(r'(?<![A-Za-z0-9._-])' + re.escape(label) + r'(?![A-Za-z0-9._-])', text))
        return {'known': missing, 'loaded': False if missing else None,
                'pid': None, 'state': 'stopped' if missing else 'unknown'}
    pid = re.search(r'^\s*pid = (\d+)\s*$', response.stdout, re.M)
    state = re.search(r'^\s*state = (\S+)', response.stdout, re.M)
    return {'known': True, 'loaded': True, 'pid': int(pid[1]) if pid else None,
            'state': state[1] if state else 'loaded'}


def require_service_known(label):
    current = service(label)
    if not current['known']:
        raise RuntimeError('Service status unknown; refusing changes / 服務狀態不明，拒絕更改')
    return current


def assert_install_complete():
    path = checked_path(STATE / 'install-transaction.json')
    if path.exists():
        record = json.loads(path.read_text())
        if not isinstance(record, dict) or record.get('phase') not in ('committed', 'rolled_back'):
            raise RuntimeError('Installation requires recovery / 安裝需要先還原')
        if record['phase'] == 'committed':
            receipt = json.loads(checked_path(STATE / 'installation.json').read_text())
            if receipt.get('transaction_id') != record.get('transaction_id'):
                raise RuntimeError('Receipt mismatch; recovery required / 安裝收據不一致')


def rpc(kind='get_scene_info', params=None, timeout=4):
    # Lifecycle/status code is incapable of replaying an execute_code command.
    if kind != 'get_scene_info' or params:
        raise ValueError('Lifecycle RPC is read-only / 連接管理只可讀取場景狀態')
    with socket.create_connection(('127.0.0.1', CONFIG['port']), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(b'{"type":"get_scene_info","params":{}}')
        data = b''
        while len(data) < 4_000_000:
            part = sock.recv(min(65536, 4_000_000 - len(data)))
            if not part:
                break
            data += part
            try:
                response = json.loads(data)
            except json.JSONDecodeError:
                continue
            if not isinstance(response, dict) or response.get('status') != 'success' or not isinstance(response.get('result'), dict):
                raise RuntimeError('Invalid Blender response / Blender 回覆無效')
            return response['result']
    raise RuntimeError('Incomplete Blender response / Blender 回覆不完整')


def blender_status():
    try:
        value = rpc()
        return {'ok': True, 'state': 'responsive', 'detail': 'Blender responded / Blender 已回應',
                'scene': value.get('name', ''), 'objects': value.get('object_count')}
    except ConnectionRefusedError:
        return {'ok': False, 'state': 'unavailable', 'detail': 'Local port not listening / 本機連接埠未啟動'}
    except Exception:
        # A busy Blender, foreign listener and bad payload must never trigger
        # spawning another Blender on this port.
        return {'ok': False, 'state': 'unknown', 'busy': True,
                'detail': 'No valid reply; preserving Blender / 未有有效回覆，保留 Blender'}


def _generation(pid, now=None):
    now = time.time() if now is None else now
    path = checked_path(STATE / 'generation.json')
    if path.stat().st_size > 4096:
        raise ValueError('Generation record oversized')
    record = json.loads(path.read_text())
    if (not isinstance(record, dict) or record.get('schema') != 1 or type(record.get('pid')) is not int or record['pid'] != pid or
            not isinstance(record.get('nonce'), str) or not re.fullmatch('[0-9a-f]{32}', record['nonce']) or
            type(record.get('started_at')) not in (int, float) or not math.isfinite(record['started_at']) or
            not 0 < record['started_at'] <= now):
        raise ValueError('Unverified process generation')
    return record


def control_plane_state(health_url, now=None, freshness_window=FRESH_WINDOW_SECONDS):
    """Compatibility API. The process generation is verified by tunnel_status."""
    try:
        text = local_get(health_url, '/metrics', MAX_METRICS_BYTES).decode('utf-8', 'strict')
    except (OSError, ValueError, UnicodeError):
        text = None
    return OBSERVER.observe(text, health_url, now, freshness=freshness_window)


def tunnel_status():
    current = service(LABEL)
    unknown = cloud_result('unknown', 'local_process_unverified')
    out = {**current, 'ok': False, 'cloud': unknown, 'generation': None,
           'detail': 'Process unknown / 通道程序未確認'}
    if not current['known']:
        return out
    if not current['loaded']:
        out['detail'] = 'Stopped / 已停止'
        return out
    if not current['pid']:
        out['detail'] = 'Loaded, no running PID; inspect startup status / 服務已載入但沒有程序'
        error_path = STATE / 'daemon-error.json'
        try:
            record = json.loads(checked_path(error_path).read_text())
            if isinstance(record, dict) and record.get('code') in ('startup_preflight_failed', 'manual_stop', 'duplicate_prevented'):
                out['startup_diagnostic'] = record['code']
        except (OSError, ValueError):
            pass
        return out
    try:
        generation = _generation(current['pid'])
        checked_path(HEALTH)
        info = HEALTH.stat()
        if info.st_size > 512 or info.st_mtime < generation['started_at'] - 1:
            raise ValueError('Stale health URL')
        url = local_url(HEALTH.read_text().strip())
        local_ready = local_get(url, '/readyz', 4096).strip() == b'ready'
        out['ok'] = local_ready
        out['generation'] = generation['nonce']
        out['detail'] = ('Local process ready, not web acceptance / 本機程序就緒，不代表網頁可用'
                         if local_ready else 'Local loop not ready / 本機迴圈未就緒')
        if local_ready:
            out['cloud'] = inspect_cloud(url, generation['nonce'], generation['started_at'], LOG)
    except (OSError, ValueError, UnicodeError):
        out['detail'] = 'Health data unknown or stale / 本機狀態資料不明或過期'
    return out


def web_status(generation, prerequisites, now=None):
    now = time.time() if now is None else now
    unknown = {'state': 'unknown', 'detail': 'Not verified in ChatGPT / 尚未在 ChatGPT 驗收',
               'source': 'none'}
    try:
        path = checked_path(STATE / 'web-acceptance.json')
        raw = path.read_bytes()
        record = json.loads(raw)
        if not isinstance(record, dict) or record.get('schema') != 1 or record.get('result') not in ('passed', 'failed'):
            return unknown
        if not prerequisites:
            invalidate_web_acceptance()
        import hashlib
        with _WEB_LOCK:
            revoked = hashlib.sha256(raw).hexdigest() in _WEB_REVOKED
        if (revoked or record.get('validator_session') != _WEB_SESSION or
                record.get('generation') != generation or not generation or not prerequisites):
            return {**unknown, 'detail': 'Revalidation required / 連線已變，需要重新驗收'}
        observed = record.get('observed_at')
        if type(observed) not in (float, int) or not math.isfinite(observed) or not 0 <= now - observed <= WEB_TTL_SECONDS:
            return {**unknown, 'detail': 'Web acceptance expired / 網頁驗收已過期'}
        passed = record['result'] == 'passed'
        return {'state': 'ok' if passed else 'failed', 'source': 'owner_reported',
                'detail': ('Owner-confirmed web test; not continuous / 使用者確認網頁測試通過，非持續監測'
                           if passed else 'Owner-reported web failure / 使用者回報網頁測試失敗'),
                'age_seconds': round(now - observed)}
    except (OSError, ValueError, TypeError):
        return unknown


def snapshot():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        b, t = pool.submit(blender_status), pool.submit(tunnel_status)
        blender, tunnel = b.result(), t.result()
    cloud = tunnel['cloud']
    prerequisites = blender['ok'] and tunnel['ok'] and cloud['state'] == 'ok'
    web = web_status(tunnel.get('generation'), prerequisites)
    return {'blender': blender, 'tunnel': tunnel, 'cloud': cloud, 'web': web,
            'local_ready': blender['ok'] and tunnel['ok'], 'cloud_ready': prerequisites,
            'ready': prerequisites and web['state'] == 'ok',
            'time': time.strftime('%H:%M:%S'), 'app_name': CONFIG['app_name']}


def record_web_acceptance(passed: bool, evidence_reference: str):
    """Explicit owner attestation, never automatic proof of a ChatGPT response."""
    if type(passed) is not bool or not isinstance(evidence_reference, str) or not evidence_reference.strip():
        raise ValueError('A real tool-response evidence reference is required / 需要真實工具回覆的證據參照')
    import hashlib
    with FileLock(STATE / 'control.lock'):
        assert_install_complete()
        current = snapshot()
        if passed and not current['cloud_ready']:
            raise RuntimeError('Local/cloud checks must pass before recording a web pass / 本機及雲端須先通過')
        atomic_json(STATE / 'web-acceptance.json', {
            'schema': 1, 'result': 'passed' if passed else 'failed',
            'observed_at': time.time(), 'generation': current['tunnel'].get('generation'),
            'validator_session': _WEB_SESSION,
            'source': 'owner_reported', 'evidence_sha256': hashlib.sha256(evidence_reference.encode()).hexdigest()})
    return {'ok': True, 'message': 'Owner observation recorded, not an automated acceptance / 已記錄使用者觀察，並非自動驗收'}


def install_service():
    expected = {'Label': LABEL, 'ProgramArguments': [PYTHON, str(ROOT / 'bridge.py'), 'daemon'],
                'WorkingDirectory': str(ROOT), 'RunAtLoad': True,
                'KeepAlive': {'SuccessfulExit': False}, 'ThrottleInterval': 60,
                'ExitTimeOut': 15, 'ProcessType': 'Background',
                'EnvironmentVariables': {'BLENDER_WEB_BRIDGE_DATA': str(DATA)},
                'StandardOutPath': str(LOG), 'StandardErrorPath': str(LOG)}
    checked_path(PLIST)
    if PLIST.exists():
        previous = plistlib.loads(PLIST.read_bytes())
        if previous == expected:
            return
        # Only a stopped, clearly-owned launch agent may receive the policy
        # update. Never rewrite another program, identity or credential setting.
        fixed = ('Label', 'ProgramArguments', 'WorkingDirectory', 'EnvironmentVariables',
                 'StandardOutPath', 'StandardErrorPath')
        if any(previous.get(key) != expected[key] for key in fixed) or require_service_known(LABEL)['loaded']:
            raise RuntimeError('Existing LaunchAgent requires reviewed migration / 現有 LaunchAgent 需要審核後遷移')
        atomic_bytes(STATE / 'backups' / ('launchagent-' + uuid.uuid4().hex + '.plist'), PLIST.read_bytes())
    atomic_bytes(PLIST, plistlib.dumps(expected))


def install_blender_service():
    path = checked_path(pathlib.Path.home() / 'Library/LaunchAgents' / (CONFIG['blender_label'] + '.plist'))
    executable = pathlib.Path(CONFIG['blender_app']) / 'Contents/MacOS/Blender'
    if path.exists():
        previous = plistlib.loads(path.read_bytes())
        args = previous.get('ProgramArguments')
        if previous.get('Label') != CONFIG['blender_label'] or not isinstance(args, list) or not args or args[0] != str(executable):
            raise RuntimeError('Existing Blender service identity differs / 現有 Blender 服務身份不同')
        return
    if not executable.is_file():
        raise RuntimeError('Blender.app not found / 找不到 Blender.app')
    isolated = RUNTIME / 'blender-userconfig'
    private_dir(isolated / 'config')
    value = {'Label': CONFIG['blender_label'],
             'ProgramArguments': [str(executable), '--factory-startup', '--python', str(ROOT / 'start_blender.py')],
             'EnvironmentVariables': {'BLENDER_USER_CONFIG': str(isolated / 'config'),
                 'BLENDER_USER_SCRIPTS': str(isolated / 'scripts'), 'BWB_CONFIG_PATH': str(CONFIG_PATH),
                 'BLENDER_MCP_SAFE_MODE': '1', 'DISABLE_TELEMETRY': 'true'},
             'RunAtLoad': True, 'KeepAlive': {'SuccessfulExit': False}, 'ThrottleInterval': 60,
             'StandardOutPath': str(STATE / 'blender.log'), 'StandardErrorPath': str(STATE / 'blender.log')}
    atomic_bytes(path, plistlib.dumps(value))


def connect():
    with FileLock(STATE / 'control.lock'):
        assert_install_complete()
        validate(CONFIG, require_ready=True)
        if not CONFIG.get('credential_configured'):
            return {'ok': False, 'message': 'Complete Setup / 請先完成設定'}
        current = require_service_known(LABEL)
        if current['loaded'] and current['pid']:
            return {'ok': True, 'message': 'Already running; no restart or operation replay / 通道已運行，不重啟或重播操作'}
        if not (RUNTIME / 'blender-mcp/.venv/bin/python').exists():
            return {'ok': False, 'message': 'Prepare components first / 請先準備元件'}
        blender = blender_status()
        if not blender['ok']:
            if blender.get('busy'):
                return {'ok': False, 'message': 'Blender response uncertain; preserved / Blender 回應不明，保持原狀'}
            bs = require_service_known(CONFIG['blender_label'])
            if bs['loaded']:
                return {'ok': False, 'message': 'Existing Blender service retained; check it locally / 保留現有 Blender 服務，請在本機檢查'}
            install_blender_service()
            bp = pathlib.Path.home() / 'Library/LaunchAgents' / (CONFIG['blender_label'] + '.plist')
            if command(['launchctl', 'bootstrap', DOMAIN, str(bp)]).returncode:
                return {'ok': False, 'message': 'Blender start not confirmed / 未能確認 Blender 啟動'}
            # Only this newly requested start is waited for. No launch/model RPC
            # is repeated and an already loaded Blender was rejected above.
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                if blender_status()['ok']:
                    break
                time.sleep(0.5)
            else:
                return {'ok': False, 'message': 'Blender start pending; no restart requested / Blender 尚未完成啟動，不會再次重啟'}
        write_profile()  # Existing profile is validated and reused byte-for-byte.
        if not current['loaded']:
            install_service()
        atomic_json(STATE / 'intent.json', {'schema': 1, 'enabled': True})
        args = (['launchctl', 'kickstart', f'{DOMAIN}/{LABEL}'] if current['loaded'] else
                ['launchctl', 'bootstrap', DOMAIN, str(PLIST)])
        response = command(args)
        if response.returncode:
            return {'ok': False, 'message': 'Launch request failed; status must be checked / 啟動要求失敗，需重新確認狀態'}
        return {'ok': True, 'message': 'Launch requested, not yet cloud/web verified / 已要求啟動，尚未通過雲端或網頁驗收'}


def disconnect():
    with FileLock(STATE / 'control.lock'):
        assert_install_complete()
        current = require_service_known(LABEL)
        # Intent is durable even if bootout fails; report that failure truthfully.
        atomic_json(STATE / 'intent.json', {'schema': 1, 'enabled': False})
        if not current['loaded']:
            return {'ok': True, 'message': 'Stopped; remains stopped at next login / 已停止，下次登入仍保持停止；Blender 不變'}
        try:
            response = command(['launchctl', 'bootout', f'{DOMAIN}/{LABEL}'], timeout=20)
        except (OSError, subprocess.SubprocessError):
            return {'ok': False, 'message': 'Stop not confirmed; Blender preserved / 停止未獲確認，Blender 保持不變'}
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            actual = service(LABEL)
            if actual['known'] and not actual['loaded']:
                return {'ok': True, 'message': 'Stopped; Blender and unsaved work preserved / 已停止通道，保留 Blender 及未存檔內容'}
            if not actual['known'] or response.returncode:
                break
            time.sleep(0.25)
        return {'ok': False, 'message': 'Stop still unconfirmed / 停止仍未獲確認；不會強制重啟 Blender'}


def daemon():
    """Exec the pinned client, leaving launchd as the only process supervisor."""
    try:
        guard = FileLock(STATE / 'daemon.lock')
        guard.__enter__()
    except (OSError, ValueError):
        return 0
    try:
        assert_install_complete()
        intent_path = checked_path(STATE / 'intent.json')
        if intent_path.exists():
            intent = json.loads(intent_path.read_text())
            if intent.get('schema') != 1 or intent.get('enabled') is not True:
                atomic_json(STATE / 'daemon-error.json', {'code': 'manual_stop'})
                return 0
        validate(CONFIG, require_ready=True)
        # No credential in logs or argv, and preflight failures exit successfully
        # so KeepAlive.SuccessfulExit=false will not create a restart storm.
        credential = load_credential(CONFIG)
        binary = checked_path(RUNTIME / 'tunnel-client/tunnel-client')
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise RuntimeError('Runtime binary unavailable')
        checked_path(HEALTH)
        HEALTH.unlink(missing_ok=True)
        atomic_json(STATE / 'generation.json', {'schema': 1, 'pid': os.getpid(),
                                               'started_at': time.time(), 'nonce': uuid.uuid4().hex})
        atomic_bytes(STATE / 'tunnel.pid', str(os.getpid()).encode())
        atomic_bytes(RUNTIME / 'tunnel-runtime.pid', str(os.getpid()).encode())
        env = os.environ.copy()
        env.update(CONTROL_PLANE_API_KEY=credential, BLENDER_HOST='127.0.0.1',
                   BLENDER_PORT=str(CONFIG['port']), BLENDER_MCP_SAFE_MODE='1',
                   DISABLE_TELEMETRY='true', BLENDER_WEB_BRIDGE_DATA=str(DATA))
        os.set_inheritable(guard.fd, True)
        os.execve(str(binary), [str(binary), 'run', '--profile', 'blender-showa',
                              '--profile-dir', str(RUNTIME / 'profiles')], env)
    except Exception:
        try:
            atomic_json(STATE / 'daemon-error.json', {'code': 'startup_preflight_failed'})
        except OSError:
            pass
        return 0
    finally:
        guard.__exit__(None, None, None)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    action = args[0] if args else 'status'
    if action == 'daemon':
        return daemon()
    functions = {'status': snapshot, 'connect': connect, 'disconnect': disconnect}
    if action not in functions:
        print('Usage: bridge.py status|connect|disconnect|daemon', file=sys.stderr)
        return 2
    try:
        response = functions[action]()
    except Exception as exc:
        # Exception text can contain paths, account information or upstream data.
        response = {'ok': False, 'error_type': type(exc).__name__,
                    'message': 'Operation failed; existing work preserved / 操作失敗，保留現有工作'}
    print(json.dumps(response, ensure_ascii=False))
    return 1 if response.get('ok') is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
