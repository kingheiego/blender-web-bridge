"""Install the pinned MCP add-on into the regular Blender profile.

This runs only in a separate, background Blender process while all user Blender
instances are closed. It never uses --factory-startup or the isolated MCP profile.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

import addon_utils
import bpy


def install():
    if not bpy.app.background:
        raise RuntimeError("Add-on preparation requires background Blender")

    wheel = Path(os.environ["BWB_MCP_WHEEL"])
    expected = os.environ["BWB_MCP_WHEEL_SHA256"]
    backup = Path(os.environ["BWB_MCP_BACKUP"])
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != expected:
        raise RuntimeError("MCP wheel checksum mismatch")
    if backup.exists() or backup.is_symlink():
        raise RuntimeError("Add-on backup destination already exists")

    with zipfile.ZipFile(wheel) as archive:
        candidates = [name for name in archive.namelist()
                      if name.endswith("blender_mcp/bundled/addon.py")]
        if len(candidates) != 1:
            raise RuntimeError("Pinned wheel has no unique Blender add-on")
        addon_bytes = archive.read(candidates[0])

    addon_dir = Path(bpy.utils.user_resource("SCRIPTS", path="addons"))
    config_dir = Path(bpy.utils.user_resource("CONFIG"))
    if addon_dir.is_symlink() or config_dir.is_symlink():
        raise RuntimeError("Linked Blender profile directories are not supported")
    target = addon_dir / "blender_mcp.py"
    preferences = config_dir / "userpref.blend"
    if target.is_symlink() or preferences.is_symlink():
        raise RuntimeError("Linked Blender profile files are not supported")
    if target.exists() and not target.is_file():
        raise RuntimeError("Existing Blender add-on target is not a file")
    if target.exists() and b'"name": "MCP for Blender"' not in target.read_bytes()[:4096]:
        raise RuntimeError("Existing Blender add-on target has a different identity")

    backup.mkdir(mode=0o700, parents=True)
    old_addon = backup / "blender_mcp.py"
    old_preferences = backup / "userpref.blend"
    if target.exists():
        shutil.copy2(target, old_addon)
    if preferences.exists():
        shutil.copy2(preferences, old_preferences)
    for saved in (old_addon, old_preferences):
        if saved.exists():
            saved.chmod(0o600)

    addon_dir.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        addon_utils.disable("blender_mcp", default_set=False)
        with tempfile.NamedTemporaryFile(dir=addon_dir, prefix=".blender_mcp-",
                                         suffix=".py", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(addon_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        temporary = None
        bpy.utils.refresh_script_paths()
        addon_utils.modules_refresh()
        addon_utils.enable("blender_mcp", default_set=True, persistent=True)
        import blender_mcp
        if (Path(blender_mcp.__file__).resolve() != target.resolve()
                or blender_mcp.ADDON_PROTOCOL_VERSION != 13
                or blender_mcp.bl_info["version"] != (1, 8)
                or "blender_mcp" not in bpy.context.preferences.addons):
            raise RuntimeError("Enabled Blender add-on does not match the pinned wheel")
        if bpy.ops.wm.save_userpref() != {"FINISHED"}:
            raise RuntimeError("Blender did not save the add-on preference")
        receipt = {
            "schema": 1,
            "blender_version": bpy.app.version_string,
            "addon_version": [1, 8],
            "protocol": 13,
            "addon_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "profile": str(config_dir.parent),
            "backup": str(backup),
        }
        (backup / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print("BWB_ADDON_READY", receipt["protocol"], receipt["addon_sha256"], flush=True)
    except Exception:
        if old_addon.exists():
            shutil.copy2(old_addon, target)
        elif target.exists():
            target.unlink()
        if old_preferences.exists():
            shutil.copy2(old_preferences, preferences)
        elif preferences.exists():
            preferences.unlink()
        raise
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    install()
