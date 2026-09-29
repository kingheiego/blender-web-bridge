# Blender Web Bridge — agent deployment

## Goal
Install the local controller and verify each connection layer without disturbing existing Blender work.
The public one-line handoff is: “On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.” Local installation can be agent-assisted; complete setup is not one-click or fully hands-off.

## Prerequisites to CHECK
- `uname -s` must return `Darwin`; locate an installed `Blender.app` (check `/Applications/Blender.app` first, then ask the user for a custom location).
- Require Python 3.10+ with a real `import tkinter`; run `./Install.command --check`.
- Check that the configured loopback port is free (`lsof -nP -iTCP:9876 -sTCP:LISTEN` for the default); never displace a listener.
- Confirm the user has an eligible ChatGPT plan/workspace/region, ChatGPT developer-mode access, and the needed Platform tunnel permissions/workspace association for Secure MCP Tunnel and custom connectors; use the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels). The user or their workspace/Platform admin handles access changes.

## Steps
1. Clone `https://github.com/kingheiego/blender-web-bridge.git` into a new directory, or use this checkout; never overwrite another checkout.
2. Run `./Install.command --check`. Before installing, inspect `install.py` and report exact target paths, existing targets, and backup/journal behavior. Run `./Install.command`, or `python3 install.py --source "$PWD" --data "$HOME/Library/Application Support/BlenderWebBridge" --desktop "$HOME/Desktop"` with a Python/Tk-capable interpreter. Report actual writes: support `app/`, Desktop `Blender Web Bridge.app`, state receipt, journal/locks, and any staging or backups. Installation starts no service.
3. Tell the user to open the installed Desktop app. Do not start or stop Blender yourself.
4. On `Setup / 設定`, use `Prepare components / 準備元件` only when both managed services are stopped and the Blender port is inactive. The app refuses active or uncertain state; report that result and do not stop a service to bypass it. Do not bypass a download hash mismatch.
5. Have the user fill `Blender.app`, `Tunnel ID / 通道 ID`, `Tool display name / 工具顯示名稱`, `Output folder / 輸出資料夾`, and the masked `Existing runtime key / 已有通道金鑰`; then use `Save setup / 儲存設定`. On `Status / 狀態`, press `Check / 檢查`. Press `Connect / 一鍵連接` only if Blender already gives a read-only response. If not, tell the user to press Connect themselves: current code may start managed Blender when its port is unavailable (`app/bridge.py:308-327`). Recheck and report separately: (1) Blender read-only query, (2) tunnel process/`/readyz`, (3) fresh cloud poll. A healthy process does not prove the cloud or web tool works.
6. In a new ChatGPT conversation after the user refreshes tools, request a real read-only `get_scene_info` result. Only after that, use the 30-second test sentence in [agent quickstart](docs/AGENT_QUICKSTART.md) in a separate new scene; confirm an actual tool call, model, and saved file while preserving existing work. The public export has no `tests/`; the suite lives in the private source. Do not claim historical tests ran here.

## NEVER
- Do not stop or restart Blender; do not clear, replace, or edit the user's existing scene or discard unsaved work.
- Do not create or request keys, tunnels, accounts, or secrets in chat. Store the runtime key only through the app's masked Keychain field; never log it.
- Do not change VPN, Tailscale, DNS, routes, or proxy. Do not expose the loopback socket beyond `127.0.0.1`.
- Do not push to the user's Git remotes.

## HUMAN ONLY
- Confirm an eligible ChatGPT plan/workspace/region, developer-mode access, Platform tunnel permissions, and workspace association using the [official tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels); the relevant admin handles access grants.
- Create your own connector app, Tunnel, and runtime key in the OpenAI/ChatGPT UI.
- Enter the runtime key yourself into the app's masked Keychain field.
- If Blender is not responsive, decide whether to press `Connect / 一鍵連接` yourself; it may start managed Blender.
- Click `Refresh tools` in the connector settings, select the connector in a NEW conversation, and approve ChatGPT consent prompts.
- Approve macOS prompts, including unidentified developer/right-click Open and Keychain access.

## Recovery
1. Check Blender. Press `Connect / 一鍵連接` only when a read-only Blender response is already available; otherwise leave the decision to the user because it may start managed Blender.
2. In the connector settings, have the user press `Refresh tools`.
3. Have the user select the connector in a NEW conversation and confirm a real read-only tool reply; see [connection recovery](docs/CONNECTION_RECOVERY.md).

## Honest limits
Tested on Apple-silicon macOS with Python 3.10/Tk. Intel, full reboot, long soak, real VPN exit-IP rotation, and all ChatGPT plans/regions are untested. Not notarized. Not affiliated with OpenAI.
