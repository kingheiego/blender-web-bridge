"""Isolated test fixtures. No macOS services, credentials or user files are used."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISOLATED = tempfile.TemporaryDirectory(prefix='bwb-rc2-module-state-')
os.environ['BLENDER_WEB_BRIDGE_DATA'] = ISOLATED.name
sys.path[:0] = [str(ROOT / 'app'), str(ROOT)]


def metrics(last=1000, errors=0):
    return (f'commands_poll_last_successful_timestamp_seconds {last}\n'
            f'commands_poll_errors_total {errors}\n')
