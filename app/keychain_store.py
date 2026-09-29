"""macOS Keychain storage through Security.framework; no secret argv or stdout."""
import ctypes
from pathlib import Path

SERVICE = b"org.blenderwebbridge.runtime-key"
NOT_FOUND = -25300


def libraries(interactive):
    sec = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
    cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    sec.SecKeychainSetUserInteractionAllowed.argtypes = [ctypes.c_bool]
    sec.SecKeychainSetUserInteractionAllowed(interactive)
    sec.SecKeychainFindGenericPassword.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p,
        ctypes.c_uint32, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]
    sec.SecKeychainFindGenericPassword.restype = ctypes.c_int32
    sec.SecKeychainAddGenericPassword.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p,
        ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32,
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    sec.SecKeychainAddGenericPassword.restype = ctypes.c_int32
    sec.SecKeychainItemModifyAttributesAndData.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    sec.SecKeychainItemModifyAttributesAndData.restype = ctypes.c_int32
    sec.SecKeychainItemFreeContent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    cf.CFRelease.argtypes = [ctypes.c_void_p]
    return sec, cf


def get(account="default"):
    sec, cf = libraries(False)
    account_bytes = account.encode()
    length = ctypes.c_uint32()
    data = ctypes.c_void_p()
    item = ctypes.c_void_p()
    status = sec.SecKeychainFindGenericPassword(
        None, len(SERVICE), SERVICE, len(account_bytes), account_bytes,
        ctypes.byref(length), ctypes.byref(data), ctypes.byref(item))
    if status == NOT_FOUND:
        return None
    if status:
        raise RuntimeError(f"Keychain unavailable ({status}); unlock it or save the key in Setup")
    try:
        return ctypes.string_at(data, length.value).decode()
    finally:
        sec.SecKeychainItemFreeContent(None, data)
        if item:
            cf.CFRelease(item)


def put(value, account="default"):
    if not value or len(value) > 4096 or "\n" in value:
        raise ValueError("Invalid key value / 金鑰格式不正確")
    sec, cf = libraries(True)
    a = account.encode()
    item = ctypes.c_void_p()
    status = sec.SecKeychainFindGenericPassword(
        None, len(SERVICE), SERVICE, len(a), a, None, None, ctypes.byref(item))
    raw = value.encode()
    buffer = ctypes.create_string_buffer(raw)
    try:
        if status == 0:
            status = sec.SecKeychainItemModifyAttributesAndData(item, None, len(raw), buffer)
        elif status == NOT_FOUND:
            status = sec.SecKeychainAddGenericPassword(
                None, len(SERVICE), SERVICE, len(a), a, len(raw), buffer, None)
        if status:
            raise RuntimeError(f"Keychain save failed ({status}); key was not exported to a file")
    finally:
        ctypes.memset(buffer, 0, len(buffer))
        if item:
            cf.CFRelease(item)


def load_credential(config):
    spec = config.get("credential", {})
    if spec.get("provider") == "keychain":
        result = get(spec.get("account", "default"))
    elif spec.get("provider") == "env_file" and config.get("allow_legacy_env_file"):
        path = Path(spec["path"])
        if path.is_symlink() or path.stat().st_mode & 0o077:
            raise RuntimeError("Legacy credential file must be private and not a symlink")
        result = None
        for line in path.read_text().splitlines():
            if line.startswith("CONTROL_PLANE_API_KEY="):
                result = line.split("=", 1)[1].strip().strip('"').strip("'")
    else:
        raise RuntimeError("Unsupported credential configuration")
    if not result:
        raise RuntimeError("Save your runtime key in Setup / 請在設定頁儲存通道金鑰")
    return result
