# Link map / 連結地圖

Use this map to move between the public guide, evidence, and upstream prerequisites. Links here point to files that are in this repository or to checked official project pages. / 這份地圖列出公開指南、證據及上游準備事項；下列連結指向 repo 內現有檔案或已核對的官方專案頁面。

**One-line agent handoff / 一句交接：**

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

This is agent-assisted local setup, **not one-click or fully hands-off**. HUMAN ONLY: confirm ChatGPT eligibility, developer-mode access, Platform tunnel permission and workspace association (ask your admin for grants); create your connector app, Tunnel and runtime key; enter the key in the masked desktop-app field; approve ChatGPT/macOS prompts; decide whether to press Connect if Blender is unresponsive (it may start managed Blender); click `Refresh tools` and select the connector in a **new conversation**. If a tunnel stops or an old conversation has no tools, check Blender, press Connect under that guard, click `Refresh tools`, then try a new conversation and confirm a real read-only reply. / 本機可由代理協助，但帳戶資格與權限、金鑰、批准及必要的 Blender 啟動決定須本人處理。通道中斷時先檢查 Blender，再連接、刷新工具、開新對話核對真實唯讀回覆。

## Start and install / 開始與安裝

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [README](../README.md) | Nine-step bilingual quick start and verified-scope table. / 雙語九步快速開始及實測範圍。 |
| [Agent quickstart — English](AGENT_QUICKSTART.md) and [AI 代理快速安裝 — 繁體中文](AGENT_QUICKSTART.zh-Hant.md) | One-line handoff and human-only steps. / 一句交接與必須親自完成的步驟。 |
| [AGENTS.md](../AGENTS.md), [CLAUDE.md](../CLAUDE.md), and [safe bootstrap](../agent-bootstrap.sh) | Agent rules, Claude Code pointer, and clone-plus-prerequisite check. / 代理規則、Claude Code 入口與安全檢查腳本。 |
| [Install with an AI — English](INSTALL_WITH_AI.md) and [交給 AI 協助安裝 — 繁體中文](INSTALL_WITH_AI.zh-Hant.md) | Copy one prompt to an AI agent for local setup, then perform the account-side steps and a simple cat test. / 複製提示詞讓 AI 協助本機安裝，再完成帳戶設定和簡單的貓模型測試。 |
| [Getting started — English](GETTING_STARTED.md) | Full, illustrated walkthrough for a first install. / 英文首次安裝全流程圖解。 |
| [入門指南 — 繁體中文](GETTING_STARTED.zh-Hant.md) | 同一流程的完整繁體中文圖解。 / Full Traditional Chinese walkthrough. |
| [FAQ — English](FAQ.md) and [常見問題 — 繁體中文](FAQ.zh-Hant.md) | Plain answers on account eligibility, local execution, risks and limits. / 帳戶資格、本機執行、風險與限制。 |
| [Connector icon fix / 連接器圖示修復](CONNECTOR_ICON_FIX.md) | Public icon asset and the remaining ChatGPT-side branding step. / 公開圖示檔與尚待完成的 ChatGPT 端品牌設定。 |
| [Annotated setup page / 圖解設定頁](SETUP_RC2.html) | Historical annotated images; follow current rc2 labels in the getting-started guides. / 舊版圖解；操作以新版指南為準。 |
| [Install.command](../Install.command) and [installer options](../install.py) | Run installation or inspect `--check` and `--rollback`; these write no services on install. / 安裝及查閱檢查、還原選項。 |
| [README_RC2](../README_RC2.md) and [繁中 RC2 說明](README_RC2.zh-Hant.md) | Standalone overviews retained for the source ZIP and installed support folder; use the root README for the current GitHub entry point. / 供原始碼 ZIP 與本機支援資料夾使用的獨立摘要；GitHub 現行入口為根目錄 README。 |

## Use, diagnose, and verify / 使用、排錯與驗證

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [Troubleshooting / 故障排解](TROUBLESHOOTING_RC2.md) | A status layer fails, the installer refuses, or rollback is incomplete. / 狀態異常、安裝被拒或還原未完成。 |
| [Connection recovery — English](CONNECTION_RECOVERY.md) and [連線恢復 — 繁體中文](CONNECTION_RECOVERY.zh-Hant.md) | Recover a stopped tunnel with Connect and refresh tools in a new ChatGPT conversation. / 按「一鍵連接」恢復通道，並在新對話重新載入工具。 |
| [2026-09-29 tunnel incident / 通道事故紀錄](INCIDENT_20260929_TUNNEL_SESSION_TERMINATED.md) | Read the observed symptom, recovery evidence, fix and limits. / 查看症狀、恢復證據、修正與未驗證事項。 |
| [Examples / 案例](EXAMPLES_RC2.md) | Read historical natural-language requests; these are not rc2 reruns. / 參考歷史自然語言案例，並非 rc2 重測。 |
| [Acceptance / 驗收](ACCEPTANCE.md) | See the earlier candidate acceptance checklist and its limits. / 查看較早階段的候選版驗收清單與限制。 |
| [Verification evidence / 實測證據](VERIFICATION_EVIDENCE.md) | See the 2026-09-29 ChatGPT web observations and screenshots. / 查看當日網頁實測紀錄及截圖。 |
| [Validation / 驗證摘要](../VALIDATION.md) | Read the verified test count and untested scope without treating them as universal proof. / 查看測試數目與未測範圍。 |
| [Network recovery / 網絡恢復](NETWORK_RECOVERY.md) | Understand process/cloud separation and retry behavior. / 理解程序、雲端狀態與重試。 |
| [Security / 安全](SECURITY_RC2.md) | Review Keychain, local-data and public-sharing boundaries. / 查閱 Keychain、本機資料及公開分享界線。 |

## Source and release / 原始碼與發佈

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [Third-party components / 第三方元件](THIRD_PARTY.md) | Identify upstream components and the pinned-download inventory. / 查看上游元件與固定版本下載表。 |
| [MIT license / MIT 授權](../LICENSE) | Read the controller source license. / 查看控制程式原始碼授權。 |
| [Changelog / 變更紀錄](../CHANGELOG.md) | See what this documentation update adds. / 查看本次文件更新。 |
| [Packaging notes / 封裝說明](../PACKAGING_NOTES.md) | See source-package limits, including no Python bundle or notarization. / 查看原始碼包及公證限制。 |
| [Pinned dependencies](../dependencies.lock.json) | Inspect exact component versions, URLs, and SHA-256 values. / 查看元件固定版本及雜湊。 |
| [Release asset inventory](../release-assets.json), [image approval](../RELEASE_IMAGE_REVIEW.json), and [web-evidence checksums](../EVIDENCE_SHA256.txt) | Check image provenance and approvals for the exact included bytes. / 核對現有圖檔的來源與批准。 |
| [Public source checksums](../PUBLIC_SOURCE_SHA256.json) | Inspect the tracked source-tree checksum inventory; `tools/build_public.py` generates a separate ZIP manifest. / 查閱目前原始碼樹的雜湊清單；封裝器另行產生 ZIP 清單。 |
| [App source](../app/), [tools](../tools/), and [icons](../assets/) | Inspect implementation, packaging checks, and artwork. / 查閱實作、封裝檢查和圖示。 |

## Upstream prerequisites / 上游準備事項

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [Blender official downloads](https://www.blender.org/download/) | Obtain Blender for your own Mac. / 自行下載 Blender。 |
| [Python official macOS downloads](https://www.python.org/downloads/macos/) | Obtain Python 3.10+ with Tk; 3.11+ recommended. / 取得有 Tk 的 Python。 |
| [OpenAI Secure MCP Tunnel documentation](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) | Check eligibility and set up your own tunnel/custom app/key. / 核對資格並建立自己的通道、App、金鑰。 |
| [OpenAI tunnel-client project](https://github.com/openai/tunnel-client) | Review the upstream client; the app downloads its own pinned, hash-verified copy. / 查看上游客戶端；App 會下載固定及核對雜湊的版本。 |
| [This GitHub repository](https://github.com/kingheiego/blender-web-bridge) | Choose **Code → Download ZIP** or copy the clone URL. / 下載 ZIP 或複製 clone 網址。 |

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
