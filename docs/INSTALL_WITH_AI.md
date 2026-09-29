# Install with an AI agent

The recommended one-line handoff for Codex or Claude Code **working on your own Mac** is:

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

An agent can check prerequisites, install the local controller, prepare pinned components, and show what remains. This is **not one-click or fully hands-off**. Only you or your admin can confirm ChatGPT plan/workspace/region eligibility, developer-mode access, Platform tunnel permission, and workspace association. Only you create your connector app and Tunnel, obtain its Tunnel ID and runtime key in the OpenAI/ChatGPT UI, enter the key in the desktop app's masked Keychain field, decide whether to press Connect if Blender is unresponsive, refresh tools, open a new ChatGPT conversation, and approve ChatGPT/macOS consent screens. The bridge is not affiliated with OpenAI and creates none of these. Never send secrets in chat. The longer prompt below is an optional expanded version of the same handoff.

## Prompt for the AI coding agent on your Mac

```text
Help me install Blender Web Bridge on my own Mac. Work in this order and report what actually happened; do not claim the web connection works until a real ChatGPT tool call succeeds.

1. Clone https://github.com/kingheiego/blender-web-bridge.git into a new local directory (never overwrite an existing checkout), or use an existing checkout. Read AGENTS.md and, if you are Claude Code, CLAUDE.md before taking installation steps; then work from the repo root.
2. Verify macOS, a local Blender.app, and Python 3.10+ with Tk. Run `./Install.command --check`; it checks Python/Tk without installing. If a prerequisite is missing, help me obtain Blender or Python from its official macOS source, handle any required human approval with me, and rerun the check. Do not claim the repo bundles Python or Blender.
3. Before installation, inspect `install.py` and tell me the exact paths it would write with its default settings (or the exact custom paths if we agreed on them). Then run `./Install.command` (or `python3 install.py` with the same chosen paths) and check its actual result and Desktop app. Do not start or stop Blender.
4. Open the installed Blender Web Bridge.app. In Setup / 設定, click Prepare components / 準備元件 only after confirming both managed services, including the tunnel, are stopped and the Blender port is inactive. If they are active or their state is uncertain, stop here and tell me what I must close or stop; do not stop Blender or a service for me. Let the app download its pinned components and verify their SHA-256 hashes. Report the actual completion or failure; never bypass a hash mismatch.
5. The public export deliberately excludes `tests/`; its suite lives in the private source. Do not run test discovery against a missing directory or present historical counts as this run's result. Use `./Install.command --check` for Python/Tk and the app's own `Check / 檢查` plus a real read-only `get_scene_info` tool call for connection verification. Report each observed layer separately.
6. Give me a short remaining-setup checklist. I must confirm account eligibility and create my own connector app and Tunnel in the OpenAI/ChatGPT UI, obtain my Tunnel ID and runtime API key, and approve any consent screens. Tell me to enter the local Blender path in `Blender.app`, my Tunnel ID in `Tunnel ID / 通道 ID`, the connector app's display name in `Tool display name / 工具顯示名稱`, and my chosen absolute local save path in `Output folder / 輸出資料夾`. I will paste my existing runtime key myself into the masked `Existing runtime key / 已有通道金鑰` field and click `Save setup / 儲存設定`; the app stores that key in macOS Keychain. If Blender is unresponsive, I alone decide whether to press Connect because it can start managed Blender. I also click Refresh tools and select the connector in a NEW conversation. Never create a key, Tunnel, connector app, or account for me; never ask me to paste a secret into chat, a command, a file, or a log. Do not claim Connect installs dependencies or completes these web-side steps.
```

`Install.command` installs the controller, but does not download runtime components or start Blender or the tunnel. **Prepare components** is a separate action. After you complete Setup, open **Status / 狀態** and click **Connect / 一鍵連接**, then **Check / 檢查**. Connect does not install Python, Blender, components, a connector app, a Tunnel, or a key. Current code can start managed Blender if its port is unavailable; an agent instructed not to start Blender must confirm a read-only Blender response before pressing Connect and leave the decision to you otherwise. For the detailed account and Mac walkthrough, see [Getting started](GETTING_STARTED.md) and the [official OpenAI Secure MCP Tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Prompt for ChatGPT after your app and Tunnel exist

First complete the account and local Setup checklist. In the desktop app, click **Connect / 一鍵連接** after checking Blender; if it is unresponsive, decide yourself whether to let Connect start managed Blender. In ChatGPT, open your app's connector settings and click **Refresh tools once**. Start a **NEW conversation**, select your app in the composer with **@ / tools**, then paste this prompt there. Complete any consent screen yourself.

```text
I created my own connector app and Secure MCP Tunnel, completed Blender Web Bridge Setup, prepared components, clicked Connect, then clicked "Refresh tools" once in my app's ChatGPT connector settings. This is a NEW conversation and I have selected my app in the composer. Use its real tools to inspect the current Blender scene, make the simplest cat from a cube in a separate scene while preserving existing work, and save it to my configured output folder. Report the actual tool result and saved path. If no tool is called, say so clearly; do not describe an imagined model as a completed test.
```

## The 30-second test request

This is a short request to send in the **new conversation** after selecting the app; it is not a promise that modeling or saving finishes in 30 seconds.

> 幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。

English: “Please do the simplest test: make a simple cat from a cube, then save it for me.”

Good means you see a real connector tool call, a small cat model appears in Blender, and a file is saved in your configured output folder. If ChatGPT makes no tool call, check the desktop app's **Status / 狀態** layers, open your app's connector settings and click **Refresh tools once**, then open a **NEW conversation** and select the app again. A conversation created while the tunnel was down may keep reporting no tools. See [Connection recovery](CONNECTION_RECOVERY.md), [連線恢復](CONNECTION_RECOVERY.zh-Hant.md), and [RC2 troubleshooting](TROUBLESHOOTING_RC2.md).
