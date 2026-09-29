# Link map / 連結地圖

Use this map to move between the public guide, evidence, and upstream prerequisites. Links here point to files that are in this repository or to checked official project pages. / 這份地圖列出公開指南、證據及上游準備事項；下列連結指向 repo 內現有檔案或已核對的官方專案頁面。

## Start and install / 開始與安裝

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [README](../README.md) | Nine-step bilingual quick start and verified-scope table. / 雙語九步快速開始及實測範圍。 |
| [Getting started — English](GETTING_STARTED.md) | Full, illustrated walkthrough for a first install. / 英文首次安裝全流程圖解。 |
| [入門指南 — 繁體中文](GETTING_STARTED.zh-Hant.md) | 同一流程的完整繁體中文圖解。 / Full Traditional Chinese walkthrough. |
| [FAQ — English](FAQ.md) and [常見問題 — 繁體中文](FAQ.zh-Hant.md) | Plain answers on account eligibility, local execution, risks and limits. / 帳戶資格、本機執行、風險與限制。 |
| [Connector icon fix / 連接器圖示修復](CONNECTOR_ICON_FIX.md) | Public icon asset and the remaining ChatGPT-side branding step. / 公開圖示檔與尚待完成的 ChatGPT 端品牌設定。 |
| [Annotated setup page / 圖解設定頁](SETUP_RC2.html) | Historical annotated images; follow current rc2 labels in the getting-started guides. / 舊版圖解；操作以新版指南為準。 |
| [Install.command](../Install.command) and [installer options](../install.py) | Run installation or inspect `--check` and `--rollback`; these write no services on install. / 安裝及查閱檢查、還原選項。 |
| [README_RC2](../README_RC2.md) and [繁中 RC2 說明](README_RC2.zh-Hant.md) | Candidate-specific background after the quick start. / 快速開始後查閱候選版細節。 |

## Use, diagnose, and verify / 使用、排錯與驗證

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [Troubleshooting / 故障排解](TROUBLESHOOTING_RC2.md) | A status layer fails, the installer refuses, or rollback is incomplete. / 狀態異常、安裝被拒或還原未完成。 |
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

## Upstream prerequisites / 上游準備事項

| Link / 連結 | When to use it / 何時使用 |
|---|---|
| [Blender official downloads](https://www.blender.org/download/) | Obtain Blender for your own Mac. / 自行下載 Blender。 |
| [Python official macOS downloads](https://www.python.org/downloads/macos/) | Obtain Python 3.10+ with Tk; 3.11+ recommended. / 取得有 Tk 的 Python。 |
| [OpenAI Secure MCP Tunnel documentation](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) | Check eligibility and set up your own tunnel/custom app/key. / 核對資格並建立自己的通道、App、金鑰。 |
| [OpenAI tunnel-client project](https://github.com/openai/tunnel-client) | Review the upstream client; the app downloads its own pinned, hash-verified copy. / 查看上游客戶端；App 會下載固定及核對雜湊的版本。 |
| [This GitHub repository](https://github.com/kingheiego/blender-web-bridge) | Choose **Code → Download ZIP** or copy the clone URL. / 下載 ZIP 或複製 clone 網址。 |
