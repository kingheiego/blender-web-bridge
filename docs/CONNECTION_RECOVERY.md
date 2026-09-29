# Recover a stopped connection

If ChatGPT replies **“Session terminated”** when you ask about Blender, the local tunnel may have stopped. The Blender scene can still be open and unchanged. A service marked “loaded” is not proof that its process is running.

## One-click recovery

1. Open **Blender Web Bridge** on your Mac. If it is already open, go to **Status**.
2. Check Blender first. If it responds to a read-only query, press **Connect**. If Blender is unresponsive, decide whether to press Connect yourself: it may start a managed Blender when the port is unavailable. If the tunnel still does not recover, press **Stop**, then **Connect** once after the same check. Stop affects the tunnel, not Blender.
3. Press **Check**. Blender should respond; the tunnel should have a running PID (`bridge.py status` shows it); the cloud layer should show a fresh successful poll when its required metrics are available. A local `/readyz` result alone does not prove that ChatGPT works.
4. In ChatGPT settings for your existing connector, press **Refresh tools**. Start a **new conversation**, select the connector, and ask a read-only question such as “What is the name of my current Blender scene?” Confirm a real tool reply before resuming edits.

If you created a conversation while the tunnel was down, it may keep an empty or unavailable tool list even after the tunnel recovers. Refreshing tools updates the connector; a new conversation lets ChatGPT load the current tool list. Repeating the question in the old conversation may continue to report “no tools.”

## If Connect does not recover it

These commands are for a technically capable Mac user. They inspect or restart only the configured tunnel service. Do not paste credentials or private logs into a public issue.

```sh
launchctl list | grep -i blender
python3 "$HOME/Library/Application Support/BlenderWebBridge/app/bridge.py" status
```

Look for your configured tunnel label in the first command and its `loaded`, `pid`, and `detail` fields in the second. If it is loaded with no PID, press **Connect** in the app. If needed, replace `YOUR_TUNNEL_LABEL` below with the exact label from your own configuration, then run:

```sh
launchctl kickstart -k "gui/$(id -u)/YOUR_TUNNEL_LABEL"
```

If the label is missing, the status is unknown, a prerequisite is failing, or you are unsure which service is yours, ask for help. Do not restart Blender or create a new tunnel or key as a recovery guess.

## Why this step exists

An earlier build could leave a tunnel stopped after a clean exit while launchd still showed it as loaded. The current controller identifies “loaded, no running PID” and tells you to press **Connect**; that button requests one start. The policy still retries abnormal exits with a 60-second throttle. It deliberately does **not** auto-restart a clean exit, because missing credentials or another startup prerequisite also cause a clean exit and must not create a restart loop. This is a one-click recovery, not a guarantee of automatic recovery after every exit.

See the [2026-09-29 incident record](INCIDENT_20260929_TUNNEL_SESSION_TERMINATED.md) and [Traditional Chinese guide](CONNECTION_RECOVERY.zh-Hant.md).

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
