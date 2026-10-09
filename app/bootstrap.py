# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
"""Install pinned, hash-verified runtime components in the user's own data folder."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
import contextlib
import stat
import tempfile
import uuid
from safeio import (FileLock, UnsafePath, atomic_bytes, atomic_json, checked_path,
                    private_dir, read_regular_bytes, fsync_dir)
from settings import ROOT, RUNTIME, STATE, CONFIG, validate


def package_file(name):
    for p in (ROOT / name, ROOT.parent / name):
        if p.exists():
            return p
    raise FileNotFoundError(name)


def architecture(value=None):
    value = value or platform.machine()
    if value in ("arm64", "aarch64"):
        return "arm64"
    if value in ("x86_64", "amd64"):
        return "x86_64"
    raise RuntimeError("Only Apple silicon and Intel Macs are supported")


def verify(path, digest):
    if hashlib.sha256(read_regular_bytes(path, max_bytes=220 * 1024 * 1024)).hexdigest() != digest:
        raise RuntimeError("Download checksum mismatch; refusing to install")


def download(spec, path):
    path = checked_path(path)
    legacy = checked_path(path.with_suffix(path.suffix + ".partial"))
    if legacy.exists():
        info = legacy.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise UnsafePath("Unsafe legacy download file / 舊下載暫存檔不安全")
    if path.exists():
        verify(path, spec["sha256"])
        return path
    private_dir(path.parent)
    fd, name = tempfile.mkstemp(prefix="." + path.name + "-", dir=path.parent)
    temporary = Path(name)
    owned = os.fstat(fd)
    try:
        count, digest = 0, hashlib.sha256()
        with os.fdopen(fd, "wb") as target:
            with urllib.request.urlopen(spec["url"], timeout=40) as source:
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    count += len(block)
                    if count > 220 * 1024 * 1024:
                        raise RuntimeError("Unexpectedly large download")
                    target.write(block)
                    digest.update(block)
            target.flush()
            os.fsync(target.fileno())
        if digest.hexdigest() != spec["sha256"]:
            raise RuntimeError("Download checksum mismatch; refusing to install")
        info = checked_path(temporary).lstat()
        if (info.st_dev, info.st_ino) != (owned.st_dev, owned.st_ino) or info.st_nlink != 1:
            raise UnsafePath("Download file identity changed / 下載暫存檔身份改變")
        checked_path(path)
        # An exclusive link publishes the verified inode without replacing a
        # destination that appeared during the request. The owned temp is removed
        # below, leaving one link; unrelated legacy .partial files are untouched.
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError:
            verify(path, spec["sha256"])
        fsync_dir(path.parent)
    finally:
        with contextlib.suppress(FileNotFoundError):
            info = temporary.lstat()
            if (info.st_dev, info.st_ino) == (owned.st_dev, owned.st_ino):
                temporary.unlink()
    return path


def extract_file(archive, basename, output):
    """Extract exactly one regular executable; never extract arbitrary archive paths."""
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            names = [x for x in z.infolist() if Path(x.filename).name == basename and not x.is_dir()]
            if len(names) != 1:
                raise RuntimeError("Ambiguous executable in download")
            if stat.S_ISLNK(names[0].external_attr >> 16):
                raise RuntimeError("Archive symlink refused")
            atomic_bytes(output, z.read(names[0]), 0o755)
    else:
        with tarfile.open(archive) as t:
            names = [x for x in t.getmembers() if Path(x.name).name == basename and x.isfile()]
            if len(names) != 1:
                raise RuntimeError("Ambiguous executable in download")
            with t.extractfile(names[0]) as f:
                atomic_bytes(output, f.read(), 0o755)
    output.chmod(0o755)


def run(args, timeout=600):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        # Public package-manager diagnostics only; no credential is passed to installers.
        raise RuntimeError((p.stderr or p.stdout)[-1500:])


def _prepare_runtime(notify=lambda message: None):
    if platform.system() != "Darwin":
        raise RuntimeError("This desktop installer is for macOS")
    # Validate every destination tree before the first mkdir/chmod/download.
    for directory in (RUNTIME, STATE, RUNTIME / "downloads",
                      RUNTIME / "tunnel-client", RUNTIME / "blender-mcp/.venv/bin",
                      RUNTIME / "blender-userconfig/scripts/addons"):
        directory = checked_path(directory)
        if directory.exists() and not directory.is_dir():
            raise UnsafePath("Expected runtime directory / 需要執行環境資料夾")
    private_dir(RUNTIME)
    private_dir(STATE)
    downloads = RUNTIME / "downloads"
    private_dir(downloads)
    lock = json.loads(package_file("dependencies.lock.json").read_text())
    arch = architecture()
    target = lock["artifacts"][arch]
    notify("Downloading and verifying uv / 下載及驗證 uv")
    uv_archive = download(target["uv"], downloads / f"uv-{lock['versions']['uv']}-{arch}.tar.gz")
    uv = RUNTIME / "uv"
    extract_file(uv_archive, "uv", uv)
    notify("Downloading and verifying tunnel-client / 下載及驗證通道程式")
    tunnel_archive = download(
        target["tunnel"], downloads / f"tunnel-client-{lock['versions']['tunnel_client']}-{arch}.zip")
    tunnel_dir = RUNTIME / "tunnel-client"
    private_dir(tunnel_dir)
    extract_file(tunnel_archive, "tunnel-client", tunnel_dir / "tunnel-client")
    notify("Preparing isolated Python and MCP / 準備隔離的 Python 和 MCP")
    venv = RUNTIME / "blender-mcp/.venv"
    python = venv / "bin/python"
    if not python.exists():
        private_dir(venv.parent)
        run([str(uv), "venv", "--python", lock["versions"]["python"], str(venv)])
    wheel = download(
        lock["mcp_wheel"],
        downloads / f"mcp_for_blender-{lock['versions']['mcp_for_blender']}-py3-none-any.whl",
    )
    run([str(uv), "pip", "install", "--python", str(python),
         "-r", str(package_file("requirements.lock")), str(wheel)])
    scripts = RUNTIME / "blender-userconfig/scripts/addons"
    private_dir(scripts)
    with zipfile.ZipFile(wheel) as z:
        names = [n for n in z.namelist() if n.endswith("blender_mcp/bundled/addon.py")]
        if len(names) != 1:
            raise RuntimeError("Pinned wheel does not contain the expected Blender add-on")
        atomic_bytes(checked_path(scripts / "blender_mcp.py"), z.read(names[0]))
    notify("Components ready / 元件已準備好")
    atomic_json(STATE / "components.json",
        {"architecture": architecture(), "versions": lock["versions"],
         "hash_verification": "PRIMARY_ARTIFACTS_PASS",
         "hash_verification_scope": ["uv", "tunnel-client", "mcp-for-blender wheel"],
         "python_transitive_hashes_verified": False})
    return {"ok": True, "message": "Components ready. Complete Setup / 元件已就緒，請完成設定"}


def blender_process_running():
    """A Blender without an MCP listener is still an open user session."""
    result = subprocess.run(["pgrep", "-x", "Blender"], capture_output=True, timeout=8)
    if result.returncode not in (0, 1):
        raise RuntimeError("Cannot verify whether Blender is open")
    return result.returncode == 0


def install_user_addon(notify=lambda message: None):
    """Enable the pinned add-on in regular Blender, preserving its preferences."""
    lock = json.loads(package_file("dependencies.lock.json").read_text())
    version = lock["versions"]["mcp_for_blender"]
    wheel = checked_path(RUNTIME / "downloads" / f"mcp_for_blender-{version}-py3-none-any.whl")
    verify(wheel, lock["mcp_wheel"]["sha256"])
    executable = checked_path(Path(CONFIG["blender_app"]) / "Contents/MacOS/Blender")
    if not executable.is_file():
        raise RuntimeError("Configured Blender executable is unavailable")
    private_dir(STATE / "backups")
    backup = checked_path(STATE / "backups" / ("regular-addon-" + uuid.uuid4().hex))
    env = os.environ.copy()
    for key in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "BLENDER_USER_ADDONS",
                "BLENDERMCP_ADDONS_DIR"):
        env.pop(key, None)
    env.update(BWB_MCP_WHEEL=str(wheel),
               BWB_MCP_WHEEL_SHA256=lock["mcp_wheel"]["sha256"],
               BWB_MCP_BACKUP=str(backup),
               BLENDER_MCP_SAFE_MODE="1", DISABLE_TELEMETRY="true")
    notify("Enabling MCP in your regular Blender / 正在日常 Blender 啟用 MCP")
    try:
        result = subprocess.run(
            [str(executable), "--background", "--python-exit-code", "1",
             "--python", str(ROOT / "enable_addon.py")],
            env=env, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("Could not finish Blender add-on setup; existing preferences preserved") from exc
    receipt = backup / "receipt.json"
    if result.returncode or not receipt.is_file():
        raise RuntimeError("Blender add-on setup failed; see its preserved backup before retrying")
    return json.loads(receipt.read_text())


def write_profile():
    validate(CONFIG, require_ready=True)
    directory = RUNTIME / "profiles"
    private_dir(directory)
    command = shlex.join([str(RUNTIME / "blender-mcp/.venv/bin/python"),
                          str(ROOT / "mcp_entry.py")])
    # JSON is a YAML-compatible document, so quoted paths and IDs stay unambiguous.
    profile = {
        "config_version": 1,
        "control_plane": {"base_url": "https://api.openai.com",
                          "tunnel_id": CONFIG["tunnel_id"],
                          "api_key": "env:CONTROL_PLANE_API_KEY"},
        "health": {"listen_addr": "127.0.0.1:0", "url_file": str(STATE / "health-url.txt")},
        "admin_ui": {"open_browser": False},
        "log": {"level": "info", "format": "json"},
        "mcp": {"commands": [{"channel": "main", "command": command}]}
    }
    path = checked_path(directory / "blender-showa.yaml")
    if path.exists():
        # Never rewrite, regenerate or normalize an existing identity/profile.
        # Legacy YAML requiring an external parser is refused rather than guessed.
        try:
            existing = json.loads(path.read_text())
        except (ValueError, OSError) as exc:
            raise RuntimeError("Existing profile needs reviewed migration; not changed") from exc
        if not isinstance(existing, dict) or not isinstance(existing.get("control_plane"), dict) or existing["control_plane"].get("tunnel_id") != CONFIG["tunnel_id"]:
            raise RuntimeError("Existing profile identity differs; not changed")
        if any(not isinstance(existing.get(key), dict) for key in ("control_plane", "health", "mcp", "log")):
            raise RuntimeError("Existing profile structure differs; not changed")
        if existing["control_plane"].get("base_url") != "https://api.openai.com":
            raise RuntimeError("Existing control-plane endpoint differs; not changed")
        if existing["mcp"].get("commands") != profile["mcp"]["commands"]:
            raise RuntimeError("Existing MCP executable binding differs; not changed")
        if existing["log"].get("format") != "json":
            raise RuntimeError("Existing log format differs; not changed")
        if existing.get("control_plane", {}).get("api_key") != "env:CONTROL_PLANE_API_KEY":
            raise RuntimeError("Existing credential binding differs; not changed")
        if existing.get("health", {}).get("listen_addr") != "127.0.0.1:0" or existing.get("health", {}).get("url_file") != str(STATE / "health-url.txt"):
            raise RuntimeError("Existing local health binding differs; not changed")
        return path
    atomic_json(path, profile)
    return path


def prepare_runtime(notify=lambda message: None):
    """Explicit setup only; do not replace runtime files used by live services."""
    from bridge import assert_install_complete, require_service_known, blender_status
    with FileLock(STATE / "control.lock"), FileLock(STATE / "daemon.lock"):
        assert_install_complete()
        for label in (CONFIG["tunnel_label"], CONFIG["blender_label"]):
            if require_service_known(label)["loaded"]:
                raise RuntimeError("Runtime preparation requires both services stopped; no service was changed")
        local = blender_status()
        if local.get("ok") or local.get("busy") or local.get("state") != "unavailable":
            raise RuntimeError("Blender port is active or uncertain; runtime left unchanged")
        if blender_process_running():
            raise RuntimeError("Close and save Blender before preparing components")
        result = _prepare_runtime(notify)
        install_user_addon(notify)
        return result


if __name__ == "__main__":
    print(json.dumps(prepare_runtime(print), ensure_ascii=False))
