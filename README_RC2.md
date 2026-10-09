# Blender Web Bridge / Blender 網頁橋接器 · 2.0.2-rc3

Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)

The current GitHub entry point is [README.md](README.md). This file remains a
standalone overview because the public source ZIP uses it as its README and the
local installer copies it into the support folder.

**One-line agent handoff / 一句交畀 AI：**

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

**Start here / 由這裡開始：** [English getting started](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/GETTING_STARTED.md) · [繁體中文入門](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/GETTING_STARTED.zh-Hant.md) · [All links / 所有連結](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/LINKS.md).

**Public prerelease; the manual Blender lifecycle passed on one Mac. / 公開測試版；手動開關與連線已於一部 Mac 實測。** See [acceptance](docs/ACCEPTANCE.md) for exact limits.

**Supported platform / 支援平台：MacBook（macOS）only / 只支援 MacBook。** Windows is not provided or tested by this project; anyone using Windows must port the source and verify it themselves. / 本 Project 不提供或驗收 Windows 版本，Windows 使用者須自行移植及測試。

This release pins OpenAI `tunnel-client` 0.0.16, Astral `uv` 0.12.24 and
`mcp-for-blender` 2.1.9, with verified download hashes. / 本版固定上述三個
版本並核對下載雜湊；準備元件不會在背景偷偷追逐上游新版。

A per-user macOS desktop controller for your existing private Blender tunnel.
One-click Connect and Stop, conservative four-layer status, and transactional updates.
用一個 macOS 視窗管理自己的 Blender 私人通道：一鍵連接／停止、四層狀態，以及可還原更新。
The full setup is not one-click or fully hands-off. HUMAN ONLY: confirm ChatGPT eligibility, developer mode, Platform tunnel permission and workspace association; create your connector app, Tunnel and key; enter the key in the masked app field; approve ChatGPT/macOS prompts; refresh tools and select the connector in a new conversation. Open Blender yourself before pressing Connect; Connect never launches Blender. / 完整設定並非一鍵全自動；帳戶資格、通道權限、App、金鑰輸入、批准、刷新工具及選擇連接器由本人處理。先自行開啟 Blender，再按 Connect；Connect 不會啟動 Blender。

## Start / 開始

You need Blender, Python 3.10+ with Tk (3.11+ recommended), and an eligible ChatGPT
account with your own existing MCP app, Tunnel ID and runtime key. Nothing here
creates a key, tunnel or account. Availability depends on account, workspace and
supported region. This source package is not notarized or self-contained.
需要 Blender、Python 3.10+ 及 Tk（建議 3.11+），以及具備相關功能的 ChatGPT 帳戶、
自己的 MCP App、既有 Tunnel ID 和 runtime key。本工具不建立帳戶、通道或金鑰，
不保證所有帳戶、地區或 Mac 均可用；這不是已公證或自帶環境的 App。

Read [Setup / 首次設定](docs/SETUP_RC2.html), then double-click `Install.command`.
Installation changes files only; it starts no services. For an update, quit the panel
and stop the tunnel first; the installer leaves Blender open. Save and close Blender
before the separate Prepare components step.
先看圖解，再雙擊安裝；安裝器不啟動服務。更新安裝器前須關閉面板及停止通道，
Blender 可保持開啟；執行「準備元件」前則須先儲存並關閉 Blender。

Open the desktop app and complete Setup. Existing identities stay unchanged.
Save and close Blender and stop the tunnel before **Prepare components**. It
downloads the pinned runtime, backs up the regular Blender add-on and
preferences, then installs and enables the add-on there. It does not stop a
running Blender or tunnel for you. Auto-Start Server makes the local socket
available when you open Blender; closing Blender leaves it closed.
打開桌面 App 並完成設定；既有身份不變。「準備元件」前先儲存並關閉 Blender，
再停止通道。此步會下載固定版本、備份日常 Blender 的插件及偏好，然後安裝
並啟用插件；不會代你停止正在運行的 Blender 或通道。往後自行開 Blender
會啟動本機 socket，關閉 Blender 後不會自動重開。

If an older install keeps reopening Blender, save its scene and Stop the tunnel.
On Setup, use **Disable old Blender auto-restart** once and confirm. It archives
only the recognized legacy service and closes its managed Blender; then use
Prepare components. / 若舊版仍會重開 Blender，先儲存場景、停止通道，在設定頁
按「停用舊版 Blender 自動重開」並確認；它只備份及停止已核實的舊服務，之後
才執行「準備元件」。

Open Blender first and let its MCP add-on start the local socket. Then press Connect.
Closing Blender closes the socket without reopening Blender. Inspect all four layers, then use your selected app in ChatGPT for
two read-only scene queries. Record the actual result in the Web acceptance tab.
按連接後檢查四層狀態，再於 ChatGPT 選擇自己的 App，執行兩次唯讀場景查詢並記錄結果。

If the tunnel stops or an old conversation has no tools, check Blender, use
Connect under the same guard, refresh tools in the connector settings, and select
the connector in a new conversation. Confirm a real read-only tool reply.

## Four independent facts / 四層各自獨立

| Layer / 層 | What it proves / 代表甚麼 |
|---|---|
| Blender | A valid local read-only response / 收到本機唯讀回覆 |
| Tunnel process / 程序 | Process identity and local `/readyz` only / 只代表程序及本機迴圈 |
| Cloud / 雲端 | Fresh, valid poll evidence without a later failure / 新鮮、有效且未被後續失敗推翻的證據 |
| ChatGPT web / 網頁 | Recent owner-reported tool result, not automated proof / 使用者回報的真實工具結果，不冒充自動驗收 |

Missing, invalid or stale metrics mean **unknown**. A later failure revokes normal
status. Web confirmation expires after five minutes, on a panel/process restart,
or any observed prerequisite failure. It does not reappear merely because the
network recovers. A region-policy 403 is not fixed by restarting or changing a key.
資料缺少、异常或過期均為**未知**；之後失敗會撤銷正常。網頁確認五分鐘後、重開面板／程序，
或觀察到前置條件失敗即失效；恢復網絡不會自動重新驗收。地區政策 403 不能靠重啟或換金鑰修復。

Stop disconnects only the tunnel and remains stopped at next login. Closing the
panel leaves a running tunnel alone. launchd is the sole supervisor; the pinned
client retries network polling. No VPN, routes, DNS, Tailscale or proxy settings
are changed. No model-changing operation is replayed by this controller.
停止只處理通道，並在下次登入維持停止；關閉面板不斷線。沿用 launchd 和固定版本客戶端的
重試，不修改 VPN／路由／DNS／Tailscale／proxy，管理流程不重播修改模型的操作。

## Read next / 文件

[繁中說明](docs/README_RC2.zh-Hant.md) · [Three historical cases / 三個歷史案例](docs/EXAMPLES_RC2.md) ·
[Troubleshooting / 排錯](docs/TROUBLESHOOTING_RC2.md) · [Acceptance / 驗收](docs/ACCEPTANCE.md) ·
[Security / 私隱](docs/SECURITY_RC2.md) · [Recovery design / 恢復設計](docs/NETWORK_RECOVERY.md)

**Verification evidence / 驗證證據：**[bilingual notes / 雙語說明](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/VERIFICATION_EVIDENCE.md) · [five screenshots, with the owner's username masked in two / 五張截圖，其中兩張已遮蓋使用者名稱](https://github.com/kingheiego/blender-web-bridge/tree/main/docs/images/evidence)

**Media completeness:** all nine original images/icon are present in this tree,
hash-matched and approved for public distribution. `tools/build_public.py` enforces
the media review gate. **圖片完整性：**九個原圖／圖示均已在本樹中，
雜湊相符並獲准公開發佈；`tools/build_public.py` 仍會檢查圖片審批。

Controller license: MIT. Pinned dependencies retain their upstream licenses.
No runtime binary or credentials are distributed. / 控制程式為 MIT；不附 runtime 或憑證。

Author / 作者: @kinghei.ego/@ai.alter (GitHub: kingheiego)

本版改為手動開關日常 Blender，固定 MCP 2.1.9。完整來源測試 207 項（205 通過、2 項既有略過）；Mac 已做真實 ChatGPT 工具查詢及關閉／重開驗證，公開來源已做全新安裝、升級與 rollback 測試。範圍與未測項目見[驗收狀態](docs/ACCEPTANCE.md)。固定檔名中的 RC2 保留以相容現有安裝器。
