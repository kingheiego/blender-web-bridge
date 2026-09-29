# Agent quickstart

No npm package exists. An agent can assist with the local install; this is not one-click or fully hands-off because account-side steps remain yours.

## The one line

Paste this single line into Codex or Claude Code on your Mac, even if you have not cloned the repo:

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

| What the agent does | What only you do |
|---|---|
| Check Mac, Blender, Python/Tk and loopback port; install controller; report exact writes. | Confirm a ChatGPT plan/workspace/region with Secure MCP Tunnel and custom connectors, developer-mode access, Platform tunnel permission, and workspace association; ask your admin for access grants. |
| Guide Setup and prepare pinned components while services are stopped. | Create your own connector app, Tunnel and runtime key in OpenAI/ChatGPT UI. |
| Check Blender, tunnel process and cloud poll separately; verify a real read-only web tool call. | Enter the key in the app's masked Keychain field; if Blender is unresponsive, decide whether to press Connect (it may start managed Blender); click Refresh tools; open a NEW conversation; approve ChatGPT and macOS prompts. |

The 30-second test is a prompt, not a guaranteed duration. Send after a real read-only scene result:

> 幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。

> Run the simplest test: make a simple cat out of a cube, then save it for me.

Recovery: check Blender first, then press `Connect / 一鍵連接`. If Blender is unresponsive, only you decide whether to press it; Connect may start managed Blender.
In ChatGPT connector settings, click `Refresh tools`.
Start a NEW conversation; see [connection recovery](CONNECTION_RECOVERY.md).

For a longer agent prompt, see [Install with an AI](INSTALL_WITH_AI.md). The app is not affiliated with OpenAI and is not notarized.

---
Watermark / 作者水印: @kinghei.ego/@ai.alter
