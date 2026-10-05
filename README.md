# Blender Web Bridge · 2.0.1-rc3

Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)

Connect the ChatGPT web app to Blender on your own Mac through an OpenAI Secure MCP Tunnel. This is a per-user macOS desktop controller and Python bridge.

**公開測試版 / Public prerelease.** 本版已修正下載暫存硬連結、runtime 目錄連結及舊式憑證檔的安全檢查。完整來源 202 項測試中 200 通過、2 略過，並已完成 Mac 隔離下載、安裝升級／精確還原和新 MCP 環境的本機唯讀驗證。[查看精確驗收範圍](docs/ACCEPTANCE.md)。這不是 OS 沙盒；請只在自己的可信任環境使用，同一 Blender 實例一次只由一個對話改寫。

**發布方式：** 本 repo 提供原始碼，供使用者自行設定私人 MCP 接駁；不是已上架官方插件商店的產品。Secure MCP Tunnel 不支援公開插件提交／分發入口，詳見[官方指南](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)。

## 實際案例與圖片

[查看完整圖集：日本遊戲中心、照片參考街景 →](docs/showcase/README.md)

圖集包含遊戲廳、照片街景及找回的黃色列車月台；附參考相片、實際提示詞、對話截圖與 Blender 渲染，亦公開人物效果不足的例子。沒有參考圖的案例則直接列出提示詞。這批是開發實測展示，不代表所有功能或所有環境已完成驗收。

## Deploy with one line / 一句交畀 AI

Paste this single line into an AI coding agent working on your Mac; the agent can clone the repo itself:

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

**Minimum requirements / 基本條件：** macOS, local Blender, Python 3.10+ with Tk (3.11+ recommended), and a ChatGPT plan/workspace/region eligible for Secure MCP Tunnel and custom connectors, with developer-mode access, Platform tunnel permission, and workspace association. The local install can be agent-assisted, but it is **not one-click or fully hands-off**. Only you or your admin can confirm and arrange account access; only you create your connector app, Tunnel and runtime key in OpenAI/ChatGPT, enter the key in the desktop app's masked Keychain field, and approve ChatGPT/macOS prompts. If Blender is unresponsive, only you decide whether to press Connect; it may start a managed Blender. You also refresh tools and open a new ChatGPT conversation. / 本機安裝可交代理協助，但帳戶資格與權限、通道、金鑰、遮罩欄輸入、批准畫面及必要時啟動 Blender，仍須本人處理；**並非一鍵全自動安裝**。

**30-second test / 30 秒測試句：** after a real read-only `get_scene_info` result in a new conversation, ask: “幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。” Ask for a separate scene, preserve existing work, and verify the real tool call and saved file. This is a short prompt, **not** a promise of completion within 30 seconds. / 先取得真實唯讀回覆，再於獨立場景測試；核對工具呼叫及存檔。

**Start here / 由這裡開始：** [Agent quickstart / 代理快速開始](docs/AGENT_QUICKSTART.md) · [繁體中文](docs/AGENT_QUICKSTART.zh-Hant.md) · [Illustrated setup / 圖解入門](docs/GETTING_STARTED.md) · [繁體中文](docs/GETTING_STARTED.zh-Hant.md) · [Recovery / 連線恢復](docs/CONNECTION_RECOVERY.md) · [繁體中文](docs/CONNECTION_RECOVERY.zh-Hant.md) · [All guides and evidence / 所有文件與證據](docs/LINKS.md).

If the tunnel stops or a conversation shows no tools: check the app's status, press Connect only after checking Blender (it may start managed Blender if the port is unavailable), refresh tools in your connector settings, and use a **new conversation**. See [connection recovery](docs/CONNECTION_RECOVERY.md). For a detailed agent prompt, see [Install with an AI](docs/INSTALL_WITH_AI.md) or [繁體中文](docs/INSTALL_WITH_AI.zh-Hant.md). The optional [`agent-bootstrap.sh`](agent-bootstrap.sh) only clones and checks prerequisites; it does not install.

## Requirements / 需求

| Requirement | 需求 |
|---|---|
| macOS and a local installation of Blender | macOS 及已安裝在本機的 Blender |
| Python 3.10+ with Tk; 3.11+ recommended | Python 3.10 或以上並有 Tk；建議 3.11 或以上 |
| An eligible ChatGPT plan, workspace and region with Secure MCP Tunnel and custom connectors | 方案、工作空間及地區均可使用 Secure MCP Tunnel 和自訂連接器的 ChatGPT |
| Your own Tunnel ID, runtime key, Blender path and output folder | 自己的 Tunnel ID、runtime key、Blender 路徑及輸出資料夾 |

## Limitations / 限制

- The source app is **not notarized** and **does not bundle Python**. / 此原始碼 App **未經 Apple 公證**，亦**不附 Python**。
- The tunnel feature is **not available to every account, workspace or region**; installing this repo cannot enable it. / **不是所有帳戶、工作空間或地區**都有通道功能；安裝此 repo 不會開通資格。
- Each user must reproduce the setup with **their own** Mac, eligible account, tunnel, key and paths. / 每位使用者均須在**自己的** Mac、合資格帳戶、通道、金鑰及路徑重做設定。
- The recorded Mac test does not cover Intel, full reboot, long soak or real VPN exit-IP rotation. / 已記錄的 Mac 測試不涵蓋 Intel、整機重啟、長時間連續運行或真實 VPN 出口 IP 輪換。

Read the [risk and limitation FAQ / 風險與限制常見問題](docs/FAQ.md) ([繁體中文](docs/FAQ.zh-Hant.md)) and the [connector icon status / 連接器圖示狀態](docs/CONNECTOR_ICON_FIX.md) before setup.

## Quick start — English

0. **What you need.** Use a Mac with [Blender](https://www.blender.org/download/), [Python 3.10+ with Tk](https://www.python.org/downloads/macos/) (3.11+ recommended), and a ChatGPT account/workspace/region that offers Secure MCP Tunnel and custom connectors. Python is **not bundled**. Follow the [official OpenAI tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) to obtain **your own** existing tunnel, Tunnel ID, runtime API key, and custom app. If your ChatGPT plan or region does not offer tunnels, **you cannot use this tool**. **See:** your own app and tunnel in ChatGPT before proceeding. **If missing:** check eligibility in the official guide; installing this repo cannot add the feature. [Prerequisites and account setup](docs/GETTING_STARTED.md#step-0--check-the-prerequisites).
1. **Download this repo.** Run `git clone https://github.com/kingheiego/blender-web-bridge.git`, or on the [repo page](https://github.com/kingheiego/blender-web-bridge) choose **Code → Download ZIP**, then unzip it. **See:** `Install.command` at the top of the downloaded folder. **If missing:** open the unzipped repo folder, not the ZIP preview. This source is **not notarized**: if macOS blocks `Install.command` as an unidentified developer, right-click it, choose **Open**, then confirm **Open**. Only do this for a copy you trust. [Download and macOS prompt](docs/GETTING_STARTED.md#step-1--download-and-open-the-repo).
2. **Install.** Double-click `Install.command`. It checks for a usable Python/Tk and writes the desktop app and local support files; it does **not** start Blender or the tunnel, download runtime components, or change accounts or network settings. **See:** an installation success result and `Blender Web Bridge.app` on your Desktop. **If missing:** read the installer message; install Python with Tk if requested, then retry. [Installation details](docs/GETTING_STARTED.md#step-2--run-installcommand).
3. **Complete Setup.** Open `Blender Web Bridge.app` on your Desktop and select **Setup / 設定**. Enter the location of your `Blender.app`, your existing Tunnel ID, your custom app's display name, and an absolute output-folder path. Enter your existing runtime API key in the masked field; the app stores it in macOS Keychain. Click **Save setup / 儲存設定**. **See:** “Saved locally.” **If missing:** check each field and make sure the tunnel is stopped; this candidate does not replace an existing ID/key binding. Never put the key in a chat or issue. [Setup fields](docs/GETTING_STARTED.md#step-3--open-the-desktop-app-and-save-setup).
4. **Prepare components once.** With **both managed services stopped**, click **Prepare components / 準備元件** in Setup. This verifies SHA-256 for uv, tunnel-client and the MCP wheel. Transitive Python packages are version-pinned, not individually hash-locked. The app never stops a running service for you. **See:** a successful completion message. **If refused:** stop the tunnel, ensure the managed Blender service is inactive, then retry; a checksum failure needs investigation, not a bypass. [Component preparation](docs/GETTING_STARTED.md#step-4--prepare-components).
5. **Connect and check four layers.** In **Status / 狀態**, check Blender first; if it is unresponsive, decide yourself whether to press **Connect / 一鍵連接**, which may start managed Blender. Click Connect once, then **Check / 檢查**. **See:** (1) Blender: a valid local read-only response; (2) tunnel process: its own process and local `/readyz` healthy; (3) cloud: **“Polling confirmed”** with fresh valid metrics; (4) ChatGPT web: only a **recent real tool result that you record** in **Web acceptance / 網頁驗收** after testing in step 6. Before that, layer 4 can correctly remain unknown. A healthy process alone does not prove cloud or web access. **If a layer is unknown or failed:** follow [troubleshooting](docs/TROUBLESHOOTING_RC2.md). [Four-layer interpretation](docs/GETTING_STARTED.md#step-5--connect-and-read-all-four-status-layers).
6. **Use it in ChatGPT.** In ChatGPT connector settings, open **your app** and click **Refresh tools once**. Start a **new conversation**, select the app with the **@ / tools** button, optionally attach a picture, and type a normal request. Start safely with “What is in my current Blender scene?” and confirm the real read-only result; repeat a read-only `get_scene_info` query before marking Web acceptance. **See:** the connector chip and a real tool reply, then record only your observation in the desktop **Web acceptance** tab. **If missing:** see [step 7](docs/GETTING_STARTED.md#step-7--fix-the-first-run-no-tools-conversation). [ChatGPT walkthrough](docs/GETTING_STARTED.md#step-6--refresh-tools-and-start-a-new-chatgpt-conversation).
7. **The first-run gotcha.** If a conversation opened while the tunnel was briefly down, it may **“show the connector but report no tools.”** Click **Refresh tools once**, then start a **NEW conversation** and select the app again; the old conversation may keep its empty tool list. **See:** the tool becomes callable in the new conversation. **If not:** check layers 1–3 and [troubleshooting](docs/TROUBLESHOOTING_RC2.md). [Evidence of this recovery](docs/VERIFICATION_EVIDENCE.md).
8. **Stop, update, or roll back.** **Stop / 停止通道** stops only the tunnel and stays stopped at next login; Blender and unsaved work remain open. Closing the panel alone leaves a running tunnel alone. For an update, stop the tunnel, quit the panel, download the new repo and run `Install.command` again. If the installer reports an incomplete transaction, keep its backup/journal files and, while stopped, run `python3 install.py --rollback` from that checkout (or supply the same `--source`, `--data`, and `--desktop` paths used for a custom install). **See:** stopped tunnel, updated desktop app, or an explicit successful rollback result. **If rollback fails:** keep the transaction files and consult [troubleshooting](docs/TROUBLESHOOTING_RC2.md). [Update and rollback details](docs/GETTING_STARTED.md#step-8--stop-update-or-roll-back).

## 快速開始 — 繁體中文

0. **先備妥條件。** 需要 Mac、[Blender](https://www.blender.org/download/)、[Python 3.10 或以上及 Tk](https://www.python.org/downloads/macos/)（建議 3.11 或以上），以及帳戶、工作空間與地區均可使用 Secure MCP Tunnel／自訂連接器的 ChatGPT。此工具**不附 Python**，亦**不建立**帳戶、通道或金鑰。按 [OpenAI 官方通道指南](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)先取得自己的通道、Tunnel ID、runtime API key 和 App。若你的 ChatGPT 方案或地區沒有通道功能，**此工具無法使用**。**應看到：**自己的 App 和通道。**若沒有：**先核對官方資格；安裝 repo 不會開通功能。[詳細說明](docs/GETTING_STARTED.zh-Hant.md#步驟-0確認所需條件)。
1. **下載 repo。** 執行 `git clone https://github.com/kingheiego/blender-web-bridge.git`，或到 [repo 頁面](https://github.com/kingheiego/blender-web-bridge)按 **Code → Download ZIP**，再解壓。**應看到：**資料夾頂層的 `Install.command`。**若沒有：**進入解壓後的資料夾，而非 ZIP 預覽。程式**未經 Apple 公證**；若 macOS 顯示「未經識別的開發者」，在可信任的副本上右鍵按 `Install.command` → **開啟** → 再確認**開啟**。[下載與開啟](docs/GETTING_STARTED.zh-Hant.md#步驟-1下載並開啟-repo)。
2. **安裝。** 雙擊 `Install.command`。它檢查 Python/Tk，寫入桌面 App 和本機支援檔；**不會**啟動 Blender 或通道、不下載執行元件，也不更改帳戶或網絡設定。**應看到：**安裝成功結果，以及桌面的 `Blender Web Bridge.app`。**若沒有：**查看安裝訊息；若提示欠缺 Python/Tk，先安裝再試。[安裝詳情](docs/GETTING_STARTED.zh-Hant.md#步驟-2執行-installcommand)。
3. **完成設定。** 開啟桌面 `Blender Web Bridge.app` → **Setup / 設定**。填入 `Blender.app` 位置、自己的既有 Tunnel ID、自訂 App 顯示名稱及完整輸出資料夾路徑。在遮罩欄輸入已有的 runtime API key；程式將其存入 macOS Keychain。按 **Save setup / 儲存設定**。**應看到：**「Saved locally」。**若沒有：**逐欄檢查並確認通道已停止；本候選版不替換既有 ID／金鑰綁定。不要把金鑰貼到對話或公開問題。[設定欄位](docs/GETTING_STARTED.zh-Hant.md#步驟-3開啟桌面-app-並儲存設定)。
4. **首次準備元件。** 確認**兩個受管理服務都未運行**，在設定頁按 **Prepare components / 準備元件**。程式核對 uv、tunnel-client 及 MCP wheel 的 SHA-256；其餘 Python 依賴固定版本，但沒有逐 wheel 雜湊鎖定；**不會替你停止正在運行的服務**。**應看到：**完成訊息。**若被拒絕：**先停止通道、確認受管理的 Blender 服務未運行，再重試；雜湊錯誤不可略過。[元件準備](docs/GETTING_STARTED.zh-Hant.md#步驟-4首次準備元件)。
5. **連接並看四層狀態。** 在 **Status / 狀態**先檢查 Blender；若無回應，由你決定是否按可能啟動受管理 Blender 的 **Connect / 一鍵連接**。按一次 Connect，再按 **Check / 檢查**。**應看到：**① Blender 有有效本機唯讀回覆；② 通道程序及本機 `/readyz` 正常；③ 雲端顯示 **「Polling confirmed」** 且 metrics 新鮮有效；④ ChatGPT 網頁須在步驟 6 真正得到工具結果後，才由你在 **Web acceptance / 網頁驗收**記錄，在此之前顯示未知屬正常。程序正常不等於雲端或網頁正常。**若有未知或失敗：**看[故障排解](docs/TROUBLESHOOTING_RC2.md)。[四層狀態](docs/GETTING_STARTED.zh-Hant.md#步驟-5連接並逐層檢查)。
6. **在 ChatGPT 使用。** 到 ChatGPT 的連接器設定打開**自己的 App**，按**一次 Refresh tools**。開一個**新對話**，用 **@／工具**按鈕選 App；可附圖，再用平常說話方式提出要求。首次先問「我目前的 Blender 場景有甚麼？」並核對真正的唯讀結果；再做一次唯讀 `get_scene_info` 查詢，才在桌面程式記錄網頁驗收。**應看到：**連接器標籤及真實工具回覆。**若沒有：**看[步驟 7](docs/GETTING_STARTED.zh-Hant.md#步驟-7修復首次使用時沒有工具的舊對話)。[ChatGPT 步驟](docs/GETTING_STARTED.zh-Hant.md#步驟-6更新工具並開啟新的-chatgpt-對話)。
7. **首次使用的常見情況。** 若對話在通道短暫中斷時建立，就可能**「顯示連接器，但回報沒有工具」（“show the connector but report no tools”）**。按**一次 Refresh tools**，開**全新對話**並重新選 App；舊對話可能仍保留空工具清單。**應看到：**新對話可呼叫工具。**若仍不能：**核對第 1–3 層並看[故障排解](docs/TROUBLESHOOTING_RC2.md)。[真實修復紀錄](docs/VERIFICATION_EVIDENCE.md)。
8. **停止、更新或還原。** **Stop / 停止通道**只停止通道，下次登入仍維持停止；Blender 和未儲存工作不會被關閉。單純關閉面板則不會斷線。更新前先停止通道、關閉面板、下載新版 repo，再執行 `Install.command`。若安裝器報告交易未完成，保留備份及紀錄，在停止狀態下於該 checkout 執行 `python3 install.py --rollback`；自訂安裝路徑時須沿用相同的 `--source`、`--data`、`--desktop`。**應看到：**通道停止、桌面 App 更新，或明確的還原成功結果。**若還原失敗：**保留交易檔並看[故障排解](docs/TROUBLESHOOTING_RC2.md)。[更新與還原](docs/GETTING_STARTED.zh-Hant.md#步驟-8停止更新與還原)。

## What actually works today / 目前實測可用

The following observations are from one Apple-silicon Mac, not a guarantee for every account, region, or machine. / 以下是單一 Apple 晶片 Mac 的觀察結果，不保證所有帳戶、地區或電腦相同。

| Capability / 功能 | Result / 結果 | Evidence / 證據 |
|---|---|---|
| Connector loads in a new conversation / 新對話載入連接器 | Verified (2026-09-29) / 已驗證 | [Verification evidence](docs/VERIFICATION_EVIDENCE.md) |
| Read-only scene query / 唯讀場景查詢 | Verified (2026-09-29) / 已驗證 | [Verification evidence](docs/VERIFICATION_EVIDENCE.md) |
| Natural-language default-folder question / 自然語言查詢預設資料夾 | Verified (2026-09-29) / 已驗證 | [Verification evidence](docs/VERIFICATION_EVIDENCE.md) |
| Natural-language save copy / 自然語言另存副本 | Verified (2026-09-29) / 已驗證；當時保存的是目前開啟的預設場景，並非較早前的模型 | [Verification evidence](docs/VERIFICATION_EVIDENCE.md) |

**Not tested / 未測：** Intel Macs; full machine reboot; long-duration soak; real VPN exit-IP rotation; notarization; all ChatGPT plans or regions. / Intel Mac、整機重啟、長時間連續運行、真實 VPN 出口 IP 輪換、公證、所有 ChatGPT 方案或地區均未測。

The 2026-10-04 full-source run executed 202 tests: 200 passed and 2 cross-filesystem cases skipped. The public checkout includes 15 targeted path-safety regressions; see [test instructions](tests/README.md). Fresh component preparation, isolated macOS install/update/exact rollback, and two real local MCP scene queries passed. These checks did not replace the owner's active installation or claim a new full ChatGPT web deployment. / 本次完整來源為 202 項：200 通過、2 項實體跨檔案系統案例略過。公開附 15 項路徑安全回歸。隔離下載、Mac 安裝升級與精確還原、本機 MCP 唯讀查詢已通過；沒有替換使用者現役安裝，也不冒稱完成 rc3 全套網頁部署驗收。

Normal client exit can still require **Connect** and a fresh conversation; the clean-exit trigger remains unconfirmed. The controller does not change VPN, routes, DNS, Tailscale or proxy and never replays model-changing operations. / 通道正常退出後仍可能需要按 Connect 及重新選取工具；直接觸發原因尚未確認，不宣稱永久自動恢復，也不重播改動模型的指令。

Controller license: [MIT](LICENSE). No runtime binary, Python installation, account, tunnel, or credential is distributed. / 控制程式採用 MIT 授權；不附執行程式、Python、帳戶、通道或憑證。

Author / 作者: @kinghei.ego/@ai.alter (GitHub: kingheiego) · https://github.com/kingheiego
