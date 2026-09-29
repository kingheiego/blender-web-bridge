# Author / 作者水印: @kinghei.ego/@ai.alter
"""Local filesystem primitives shared by the installer and desktop controller.

Locks are never unlinked. Refuse symlinks (including dangling ones), special
files and multiply-linked lock files. These are cooperative-update guards, not
an isolation boundary against a hostile process already running as this user.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import stat
import tempfile
from pathlib import Path


class UnsafePath(ValueError):
    pass


def checked_path(value) -> Path:
    path = Path(os.path.abspath(os.path.expanduser(str(value))))
    for component in reversed((path,) + tuple(path.parents)):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise UnsafePath('Symlink path refused / 不接受符號連結路徑')
        if component != path and not stat.S_ISDIR(info.st_mode):
            raise UnsafePath('Parent is not a directory / 上層不是資料夾')
    return path


def private_dir(path: Path) -> Path:
    path = checked_path(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    checked_path(path)
    if not path.is_dir():
        raise UnsafePath('Expected directory / 需要資料夾')
    # Do not chmod an arbitrary pre-existing user-specified parent.
    return path


def fsync_dir(path: Path) -> None:
    fd = os.open(checked_path(path), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def identity(path: Path):
    path = checked_path(path)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
        raise UnsafePath('Special file refused / 不接受特殊檔案')
    return [info.st_dev, info.st_ino]


class FileLock:
    def __init__(self, path):
        self.path, self.fd = Path(path), None

    def __enter__(self):
        private_dir(self.path.parent)
        checked_path(self.path)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid():
                raise UnsafePath('Unsafe lock file / 鎖檔不安全')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(fd)
            raise
        self.fd = fd
        return self

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        return False


def atomic_bytes(path: Path, content: bytes, mode=0o600) -> None:
    path = checked_path(path)
    private_dir(path.parent)
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        checked_path(path)
        os.replace(temporary, path)
        fsync_dir(path.parent)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


def atomic_json(path: Path, value: dict) -> None:
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode())


def rename_owned(source: Path, destination: Path, expected: list) -> None:
    """Atomic same-filesystem rename only; EXDEV is never emulated by copy/delete."""
    source, destination = checked_path(source), checked_path(destination)
    if identity(source) != expected:
        raise UnsafePath('Transaction ownership changed / 安裝目標擁有權已改變')
    if identity(destination) is not None:
        raise UnsafePath('Destination already exists / 目的地已有檔案')
    left = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    right = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.rename(source.name, destination.name, src_dir_fd=left, dst_dir_fd=right)
        os.fsync(left)
        os.fsync(right)
    finally:
        os.close(left)
        os.close(right)
