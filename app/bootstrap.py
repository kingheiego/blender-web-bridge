# Author / 作者水印: @kinghei.ego/@ai.alter
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
from safeio import FileLock, atomic_bytes, atomic_json, checked_path
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
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
        raise RuntimeError("Download checksum mismatch; refusing to install")


def download(spec, path):
    checked_path(path)
    checked_path(path.with_suffix(path.suffix + ".partial"))
    if path.exists():
        verify(path, spec["sha256"])
        return path
    temporary = path.with_suffix(path.suffix + ".partial")
    count = 0
    with urllib.request.urlopen(spec["url"], timeout=40) as source, temporary.open("wb") as target:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            if count > 220 * 1024 * 1024:
                raise RuntimeError("Unexpectedly large download")
            target.write(block)
    verify(temporary, spec["sha256"])
    os.replace(temporary, path)
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
    RUNTIME.mkdir(parents=True, exist_ok=True)
    RUNTIME.chmod(0o700)
    STATE.mkdir(parents=True, exist_ok=True)
    downloads = RUNTIME / "downloads"
    downloads.mkdir(exist_ok=True)
    lock = json.loads(package_file("dependencies.lock.json").read_text())
    target = lock["artifacts"][architecture()]
    notify("Downloading and verifying uv / 下載及驗證 uv")
    uv_archive = download(target["uv"], downloads / "uv.tar.gz")
    uv = RUNTIME / "uv"
    extract_file(uv_archive, "uv", uv)
    notify("Downloading and verifying tunnel-client / 下載及驗證通道程式")
    tunnel_archive = download(target["tunnel"], downloads / "tunnel-client.zip")
    tunnel_dir = RUNTIME / "tunnel-client"
    tunnel_dir.mkdir(exist_ok=True)
    extract_file(tunnel_archive, "tunnel-client", tunnel_dir / "tunnel-client")
    notify("Preparing isolated Python and MCP / 準備隔離的 Python 和 MCP")
    venv = RUNTIME / "blender-mcp/.venv"
    python = venv / "bin/python"
    if not python.exists():
        venv.parent.mkdir(exist_ok=True)
        run([str(uv), "venv", "--python", lock["versions"]["python"], str(venv)])
    wheel = download(lock["mcp_wheel"], downloads / "mcp_for_blender-2.1.0-py3-none-any.whl")
    run([str(uv), "pip", "install", "--python", str(python),
         "-r", str(package_file("requirements.lock")), str(wheel)])
    scripts = RUNTIME / "blender-userconfig/scripts/addons"
    scripts.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(wheel) as z:
        names = [n for n in z.namelist() if n.endswith("blender_mcp/bundled/addon.py")]
        if len(names) != 1:
            raise RuntimeError("Pinned wheel does not contain the expected Blender add-on")
        atomic_bytes(checked_path(scripts / "blender_mcp.py"), z.read(names[0]))
    notify("Components ready / 元件已準備好")
    atomic_json(STATE / "components.json",
        {"architecture": architecture(), "versions": lock["versions"],
         "hash_verification": "PASS"})
    return {"ok": True, "message": "Components ready. Complete Setup / 元件已就緒，請完成設定"}


def write_profile():
    validate(CONFIG, require_ready=True)
    directory = RUNTIME / "profiles"
    directory.mkdir(parents=True, exist_ok=True)
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
        return _prepare_runtime(notify)


if __name__ == "__main__":
    print(json.dumps(prepare_runtime(print), ensure_ascii=False))
