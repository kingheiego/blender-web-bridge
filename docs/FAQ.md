# Frequently asked questions

[繁體中文版](FAQ.zh-Hant.md) · [Getting started](GETTING_STARTED.md) · [Security details](SECURITY_RC2.md)

## Will OpenAI or ChatGPT ban my account for using this?

This uses OpenAI's supported [Secure MCP Tunnel and custom-connector developer feature](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels). It is not a hack or jailbreak, and it does not bypass billing or access controls. Using a documented developer feature is not, by itself, a violation. Still, a custom app can show **dev mode / DEVELOPMENT** review status, tunnel access depends on your plan, workspace and region, and you are responsible for code you allow it to run. We cannot promise OpenAI's policies will never change. This project is not affiliated with or endorsed by OpenAI.

## Why can it control my Mac without Codex compute or tokens?

The model runs on OpenAI's servers in your normal ChatGPT session. The tunnel carries requests; the local MCP server on **your Mac** executes Blender calls. This workflow does not use Codex tokens or the Codex runtime. Your Mac must stay awake and online while it works.

## What are the real risks?

- `execute_blender_code` runs arbitrary Python **inside your Blender process**. That is a feature with real power: a bad call can change or lose work.
- The optional upstream **Safe Mode**, enabled by this controller's runtime, blocks imports such as `os`, `sys`, `subprocess` and `socket` and dangerous interpreter escapes on the model-code path. It is a guard, **not a sandbox around Blender**. Do not treat it as permission to run untrusted code.
- The Blender loopback socket has **no authentication**. Any local process on your Mac could call it. Keep it bound to loopback; **never expose the socket to your network**.
- Asset names or descriptions read by the model can contain **prompt injection** that tries to steer it toward harmful code. Safe Mode reduces this route but does not make it impossible.
- Scene data, viewport screenshots and paths you ask ChatGPT about may be sent to ChatGPT. Do not ask it to inspect private content you do not want to share.
- The runtime API key is stored in **macOS Keychain**, not this repository. Do not put it in a prompt, issue or screenshot.
- The app is **not notarized**, so macOS may warn on first run. Open only a copy you trust.
- Protect **unsaved Blender work**. Do not use **Prepare components** while you are modelling; the controller may refuse the action rather than stop a running service for you. Save and inspect your scene before risky actions.

## What has not been tested?

The recorded scope is Apple-silicon macOS with Python 3.10+ and Tk. It has **not** been tested on Intel Macs, across a full machine reboot, in a long-duration soak, with real VPN exit-IP rotation, for notarization, or on every ChatGPT plan, region or workspace. The controller needs **no fixed public IP** and does **not change VPN, routes, DNS, Tailscale or proxy**. It cannot guarantee that a particular VPN exit is accepted by the service. See [verification evidence](VERIFICATION_EVIDENCE.md).

## What must I check or tune for my own Mac?

| Check | Where to set or verify it |
|---|---|
| Python **3.10+ with Tk**; 3.11+ recommended | Install separately, then run `./Install.command --check` in the repo folder. Python is not bundled. |
| Your `Blender.app` location | **Setup / 設定 → Blender.app** in the desktop app. |
| A free loopback port | Default **9876**. Check or change `port` in `config.json` under your own `~/Library/Application Support/BlenderWebBridge/` directory while services are stopped; there is no port field in the desktop Setup tab. Keep it loopback-only. |
| Your own Tunnel ID and runtime API key | First-time **Setup / 設定** fields; paste the key only into the masked field. Existing identity/key replacement is not supported by this rc2 controller. |
| Your output folder | **Setup / 設定 → Output folder / 輸出資料夾**; use a writable absolute path on your Mac. |
| Mac stays awake and online | Check macOS power/sleep settings and your connection before starting a long task. |

Every user needs their own eligible ChatGPT setup, tunnel, key and local paths; another person's working setup does not transfer to your Mac.

## Is it safe to leave the tunnel running?

The Blender socket listens only on loopback, and the tunnel connects **outbound** to OpenAI. That limits network exposure but is not a guarantee against local processes or bad tool calls. **Stop / 停止通道** stops only the tunnel and keeps Blender open. Closing the desktop panel **does not disconnect** it. Stop the tunnel when you do not need ChatGPT access, and save your Blender work normally.

---
Watermark / 作者水印: @kinghei.ego/@ai.alter
