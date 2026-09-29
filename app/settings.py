# Author / 作者水印: @kinghei.ego/@ai.alter
"""Per-user configuration. No account identifiers belong in the source tree."""
import json
import os
from pathlib import Path
import re
from safeio import atomic_json, checked_path

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("BLENDER_WEB_BRIDGE_DATA",
                          str(Path.home() / "Library/Application Support/BlenderWebBridge"))).expanduser()
CONFIG_PATH = DATA / "config.json"


def defaults(home=None, data=None):
    home = Path(home) if home is not None else Path.home()
    data = Path(data) if data is not None else DATA
    return {
        "schema_version": 1,
        "runtime_root": str(data / "runtime"),
        "state_root": str(data / "state"),
        "blender_app": "/Applications/Blender.app",
        "blender_label": "org.blenderwebbridge.blender",
        "tunnel_label": "org.blenderwebbridge.tunnel",
        "port": 9876,
        "tunnel_id": "",
        "app_name": "Blender (My Mac)",
        "output_root": str(home / "Documents/BlenderWebBridge/output"),
        "credential": {"provider": "keychain", "account": "default"},
        "credential_configured": False,
    }


def load():
    value = defaults()
    checked_path(CONFIG_PATH)
    if CONFIG_PATH.exists():
        existing = json.loads(CONFIG_PATH.read_text())
        if not isinstance(existing, dict):
            raise ValueError("Config must be a JSON object / 設定必須是物件")
        value.update(existing)
    validate(value)
    return value


def validate(value, require_ready=False):
    if not isinstance(value, dict):
        raise ValueError("Config must be an object")
    forbidden = {"api_key", "password", "secret", "access_token", "refresh_token"}
    def inspect(obj):
        if isinstance(obj, dict):
            if any(str(k).lower() in forbidden for k in obj):
                raise ValueError("Secret material is not allowed in config.json")
            for item in obj.values():
                inspect(item)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                inspect(item)
        elif isinstance(obj, str) and obj.startswith(("sk-proj-", "sk-svcacct-")):
            raise ValueError("Enter keys only in the masked key field")
    inspect(value)
    if type(value.get("port")) is not int or not 1024 <= value["port"] <= 65535:
        raise ValueError("Port must be between 1024 and 65535 / 連接埠格式不正確")
    tunnel = value.get("tunnel_id", "")
    if not isinstance(tunnel, str):
        raise ValueError("Tunnel ID must be text")
    if tunnel and not re.fullmatch(r"tunnel_[A-Za-z0-9_-]{16,128}", tunnel):
        raise ValueError("Enter a valid Tunnel ID, not an API key / 請填 Tunnel ID")
    if require_ready and not tunnel:
        raise ValueError("Complete Setup first / 請先完成設定頁")
    for key in ("runtime_root", "state_root", "blender_app", "output_root"):
        if not isinstance(value.get(key), str) or not Path(value[key]).is_absolute():
            raise ValueError(f"{key} must be an absolute path / 必須使用完整路徑")
    for key in ("blender_label", "tunnel_label"):
        if not isinstance(value.get(key), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}", value[key]):
            raise ValueError("Invalid service label")
    if value["blender_label"] == value["tunnel_label"]:
        raise ValueError("Service labels must be distinct")
    if not isinstance(value.get("credential"), dict):
        raise ValueError("Invalid credential reference")
    if not isinstance(value.get("app_name"), str) or not 1 <= len(value["app_name"]) <= 200:
        raise ValueError("App name must be non-empty text")
    if type(value.get("credential_configured")) is not bool:
        raise ValueError("Credential state must be a boolean")
    provider = value.get("credential", {}).get("provider")
    if provider not in ("keychain", "env_file"):
        raise ValueError("Unsupported credential provider")
    # env_file is for an explicitly approved local migration, never a public default.
    if provider == "env_file" and not value.get("allow_legacy_env_file", False):
        raise ValueError("Legacy env-file storage requires explicit local opt-in")


def save(value):
    """Caller holds control.lock and has verified the service is stopped."""
    validate(value)
    # Keep all existing identity, storage and service bindings unchanged in this
    # release. Creating an initial configuration is allowed; migrations are not.
    if CONFIG_PATH.exists():
        for key in ("tunnel_id", "credential", "blender_label", "tunnel_label",
                    "runtime_root", "state_root"):
            if CONFIG.get("tunnel_id") and value.get(key) != CONFIG.get(key):
                raise ValueError("Existing identity/storage is immutable / 不可更改既有身份或儲存位置")
    atomic_json(CONFIG_PATH, value)
    CONFIG.clear()
    CONFIG.update(value)


CONFIG = load()
STATE = Path(CONFIG["state_root"])
RUNTIME = Path(CONFIG["runtime_root"])
