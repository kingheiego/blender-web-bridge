# Blender Web Bridge — agent deployment

## Goal
Install the local controller and verify each connection layer without disturbing existing Blender work.
The supported product target is **MacBook (macOS) only**. Do not treat Windows as a required setup or test target; Windows users must port and validate the source themselves.
The public one-line handoff is: “On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.” Local installation can be agent-assisted; complete setup is not one-click or fully hands-off.

## Prerequisites to CHECK
- `uname -s` must return `Darwin`; locate an installed `Blender.app` (check `/Applications/Blender.app` first, then ask the user for a custom location).
- Require Python 3.10+ with a real `import tkinter`; run `./Install.command --check`.
- Check that the configured loopback port is free (`lsof -nP -iTCP:9876 -sTCP:LISTEN` for the default); never displace a listener.
- Confirm the user has an eligible ChatGPT plan/workspace/region, ChatGPT developer-mode access, and the needed Platform tunnel permissions/workspace association for Secure MCP Tunnel and custom connectors; use the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels). The user or their workspace/Platform admin handles access changes.

## Steps
1. Clone `https://github.com/kingheiego/blender-web-bridge.git` into a new directory, or use this checkout; never overwrite another checkout.
2. Run `./Install.command --check`. Before installing, inspect `install.py` and report exact target paths, existing targets, and backup/journal behavior. Run `./Install.command`, or `python3 install.py --source "$PWD" --data "$HOME/Library/Application Support/BlenderWebBridge" --desktop "$HOME/Desktop"` with a Python/Tk-capable interpreter. Report actual writes: support `app/`, Desktop `Blender Web Bridge.app`, state receipt, journal/locks, and any staging or backups. The bundle filename stays stable; its visible name is `Blender Web Bridge / Blender 網頁橋接器`. Installation starts no service.
3. Tell the user to open the installed Desktop app. Do not start or stop Blender yourself.
4. Have the user fill the configured `Blender.app` path, `Tunnel ID / 通道 ID`, `Tool display name / 工具顯示名稱`, `Output folder / 輸出資料夾`, and masked `Existing runtime key / 已有通道金鑰`; then use `Save setup / 儲存設定`. The Blender path must be correct before preparing components.
5. Save and close Blender, stop the tunnel, then use `Prepare components / 準備元件` in Setup. For an older install that keeps reopening Blender, the user must first save the scene, stop the tunnel, and confirm Setup's **Disable old Blender auto-restart** action; it archives only a recognized legacy service. Prepare components installs the pinned runtime and enables the add-on in the regular Blender profile, preserving a versioned backup of the existing add-on and preferences. The app refuses an active or uncertain Blender/service state; do not bypass that guard or a download hash mismatch.
6. Ask the user to open Blender. On `Status / 狀態`, press `Check / 檢查`, then `Connect / 一鍵連接` only after Blender gives a read-only response. Connect never starts Blender. Recheck separately: (1) Blender read-only query, (2) tunnel process/`/readyz`, (3) fresh cloud poll. A healthy process does not prove the cloud or web tool works.
7. In a new ChatGPT conversation after the user refreshes tools, request a real read-only `get_scene_info` result. Only after that, use the 30-second test sentence in [agent quickstart](docs/AGENT_QUICKSTART.md) in a separate new scene; confirm an actual tool call, model, and saved file while preserving existing work. The public checkout contains only selected tests; the complete suite lives in the project source. Do not claim historical tests ran here.

## NEVER
- Do not stop or restart Blender; do not clear, replace, or edit the user's existing scene or discard unsaved work.
- Do not create or request keys, tunnels, accounts, or secrets in chat. Store the runtime key only through the app's masked Keychain field; never log it.
- Do not change VPN, Tailscale, DNS, routes, or proxy. Do not expose the loopback socket beyond `127.0.0.1`.
- Do not push to the user's Git remotes.

## HUMAN ONLY
- Confirm an eligible ChatGPT plan/workspace/region, developer-mode access, Platform tunnel permissions, and workspace association using the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels); the relevant admin handles access grants.
- Create your own connector app, Tunnel, and runtime key in the OpenAI/ChatGPT UI.
- Enter the runtime key yourself into the app's masked Keychain field.
- Open and close Blender yourself. `Connect / 一鍵連接` starts only the tunnel after Blender responds.
- Click `Refresh tools` in the connector settings, select the connector in a NEW conversation, and approve ChatGPT consent prompts.
- Approve macOS prompts, including unidentified developer/right-click Open and Keychain access.

## Recovery
1. Ask the user to open Blender and wait for its MCP add-on to respond. Press `Connect / 一鍵連接` only after a read-only Blender response is available.
2. In the connector settings, have the user press `Refresh tools`.
3. Have the user select the connector in a NEW conversation and confirm a real read-only tool reply; see [connection recovery](docs/CONNECTION_RECOVERY.md).

## Honest limits
Tested on Apple-silicon macOS with Python 3.10/Tk. Intel, full reboot, long soak, real VPN exit-IP rotation, and all ChatGPT plans/regions are untested. Not notarized. Not affiliated with OpenAI.
