# Claude Code

Read and follow [AGENTS.md](AGENTS.md) for Blender Web Bridge deployment and verification.

This product supports **MacBook (macOS) only**. Windows users must adapt and verify their own port; do not promise Windows setup or testing.

The same one-line handoff used by Codex and Claude Code is: “On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.” This is agent-assisted local installation, not one-click or fully hands-off setup. HUMAN ONLY: confirm ChatGPT plan/workspace/region eligibility, developer-mode access, Platform tunnel permission and workspace association (with an admin where needed); create the connector app, Tunnel and key; enter the key in the masked Keychain field; decide whether to press Connect if Blender is unresponsive; refresh tools; select the connector in a new ChatGPT conversation; approve ChatGPT/macOS prompts.

NEVER stop/restart Blender or clear/edit an existing scene; ask for or log keys; change VPN/Tailscale/DNS/proxy; expose the loopback socket; or push to the user's Git remotes. The user opens Blender manually before `Connect`; the button never starts Blender. Follow the lifecycle guard in `AGENTS.md`.

For recovery, check Blender first, use Connect only under that guard, then have the user click `Refresh tools` and select the connector in a NEW conversation. Confirm a real read-only tool result; see [connection recovery](docs/CONNECTION_RECOVERY.md).
