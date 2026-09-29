#!/usr/bin/env bash
# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
# Safe bootstrap: only clone to a new directory, run Install.command --check,
# and print the exact agent handoff line from docs/AGENT_QUICKSTART.md.
# No install, service/Blender access, VPN/network changes, keys, deletion,
# remote-code piping, or overwrite of an existing directory.
set -eu

if [ "$#" -gt 1 ]; then
  printf 'Usage: %s [new-clone-directory]\n' "$0" >&2
  exit 2
fi

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
target="${1:-$HOME/Downloads/blender-web-bridge}"
parent="$(cd "$(dirname "$target")" && pwd -P)" || {
  printf 'Target parent directory does not exist: %s\n' "$target" >&2
  exit 2
}
target_dir="$parent/$(basename "$target")"
case "$target_dir" in
  "$source_dir"|"$source_dir"/*)
    printf 'Refusing to clone inside the source repo: %s\n' "$target_dir" >&2
    exit 2 ;;
esac
if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then
  printf 'Target already exists; nothing overwritten: %s\n' "$target_dir" >&2
  exit 2
fi

git clone -- https://github.com/kingheiego/blender-web-bridge.git "$target_dir"
printf 'Prerequisite check in %s:\n' "$target_dir"
check_status=0
(cd "$target_dir" && ./Install.command --check </dev/null) || check_status=$?
printf 'Agent handoff line (paste into an AI coding agent on this Mac):\n'
printf '%s\n' "On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps."
exit "$check_status"
