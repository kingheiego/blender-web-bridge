# 交給 AI 代理協助安裝

給在自己 Mac 上工作的 Codex 或 Claude Code，建議使用以下同一句交接：

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

代理可以檢查先決條件、安裝本機控制程式、準備固定版本元件，並列出餘下步驟；這**不是一鍵全自動安裝**。你或管理員須確認 ChatGPT 方案／工作空間／地區資格、開發者模式、Platform 通道權限及工作空間關聯。只有你可在 OpenAI／ChatGPT 建立自己的 connector app 和 Tunnel 並取得 Tunnel ID／runtime key、在桌面程式遮罩欄輸入 key、Blender 無回應時決定是否按 Connect、刷新工具、開新對話，以及確認 ChatGPT／macOS 同意畫面。本工具與 OpenAI 無關，亦不會建立上述帳戶資料。不要在對話中建立或索取秘密；程式會把遮罩欄內的 key 存入 macOS Keychain。下方長提示詞只是同一交接的詳細版。

## 給自己 Mac 上 AI coding agent 的提示詞

```text
請幫我在自己的 Mac 安裝 Blender Web Bridge。按以下次序執行並如實回報；未見到 ChatGPT 真正呼叫工具前，不可聲稱網頁連接已通過。

1. 將 https://github.com/kingheiego/blender-web-bridge.git clone 到一個全新的本機資料夾，不可覆蓋現有 checkout；或使用已有 checkout。安裝前先讀 AGENTS.md；如你是 Claude Code，亦須讀 CLAUDE.md。之後在 repo 根目錄工作。
2. 核對 macOS、本機 Blender.app、Python 3.10 或以上及 Tk。執行 `./Install.command --check`；這只檢查 Python/Tk，不會安裝。若欠缺條件，協助我從 Blender 或 Python 的官方 macOS 來源取得軟件；需要本人批准的畫面交給我，然後重做檢查。不可聲稱 repo 已附 Python 或 Blender。
3. 安裝前先查看 `install.py`，告訴我預設實際會寫入哪些路徑；如已協定自訂路徑，列明那些路徑。然後執行 `./Install.command`（或沿用選定路徑執行 `python3 install.py`），核對真正結果及桌面 App。不要啟動或停止 Blender。
4. 開啟已安裝的 Blender Web Bridge.app。在 Setup / 設定，先儲存並關閉 Blender、停止通道，並確認 Blender 連接埠未在使用後，才按 Prepare components / 準備元件。若服務仍運行或狀態不明，先停下並告訴我須自行關閉或停止甚麼；不要代我停止 Blender 或服務。讓 App 下載固定版本元件、核對 SHA-256，並備份及啟用日常 Blender 插件，如實回報完成或失敗；不可略過雜湊錯誤。
5. 公開版本刻意不包含 `tests/`；測試套件只在私人原始碼。不可對不存在的目錄執行測試探索，也不可把歷史測試數字當作這次結果。以 `./Install.command --check` 檢查 Python/Tk，再用 App 的 `Check / 檢查` 及真實唯讀 `get_scene_info` 工具呼叫核對連線；分別如實回報每一層。
6. 給我一份簡短的餘下設定清單。我須確認帳戶資格，並在 OpenAI／ChatGPT 介面自行建立 connector app 與 Tunnel、取得自己的 Tunnel ID 和 runtime API key，以及確認任何同意畫面。請指出：本機 Blender 路徑填入 `Blender.app`；Tunnel ID 填入 `Tunnel ID / 通道 ID`；連接器 App 顯示名稱填入 `Tool display name / 工具顯示名稱`；我選定的本機絕對儲存路徑填入 `Output folder / 輸出資料夾`。我會親自在遮罩的 `Existing runtime key / 已有通道金鑰` 欄填入已有 runtime key，再按 `Save setup / 儲存設定`；App 會把 key 存入 macOS Keychain。我會先自行開 Blender，確認 MCP 插件有回應後再按 Connect；Connect 不會啟動 Blender；Refresh tools 及在新對話選 App 亦由我完成。不可代我建立 key、Tunnel、connector app 或帳戶；不可要求我把秘密貼到對話、指令、檔案或 log。不可聲稱 Connect 會安裝依賴或完成網頁側設定。
```

`Install.command` 只安裝控制程式，不下載執行元件，也不啟動 Blender 或通道；**Prepare components / 準備元件** 是獨立步驟。完成 Setup 後，在 **Status / 狀態**按 **Connect / 一鍵連接**，再按 **Check / 檢查**。Connect 不會安裝 Python、Blender、元件、connector app、Tunnel 或 key；Connect 不會啟動 Blender；按 Connect 前必須先開 Blender 並取得唯讀回覆。詳見[繁體中文入門指南](GETTING_STARTED.zh-Hant.md)及 [OpenAI 官方 Secure MCP Tunnel 指南](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)。

## 已建立自己的 App 和 Tunnel 後，給 ChatGPT 的提示詞

先完成帳戶及本機 Setup 清單，檢查 Blender 後在桌面 App 按 **Connect / 一鍵連接**；若 Blender 無回應，先自行開 Blender 並等候 MCP 插件啟動；Connect 不會啟動 Blender。在 ChatGPT 打開你的 App 的 connector settings，按**一次 Refresh tools**；開**全新對話**，在輸入欄用 **@／工具**選好 App，然後才把以下提示詞貼進該對話。任何同意畫面由你親自確認。

```text
我已自行建立 connector app 及 Secure MCP Tunnel，完成 Blender Web Bridge 本機 Setup、準備元件、在桌面程式按 Connect，亦已在 ChatGPT 的 App connector settings 按一次「Refresh tools」。這是全新對話，我已在輸入欄選好我的 App。請真正呼叫工具先查看目前 Blender 場景，再在獨立場景由立方體做一隻最簡單的貓、保留現有工作，最後存入我設定的輸出資料夾。請回報實際工具結果及儲存路徑。若沒有呼叫到工具，請如實說明，不要把想像中的模型當成測試成功。
```

## 30 秒測試句子

這是一句可以快速送出的測試要求，**不保證**建模和儲存會在 30 秒完成。請在選好 App 的**新對話**傳送：

> 幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。

英文版：“Please do the simplest test: make a simple cat from a cube, then save it for me.”

真正通過的樣子是：ChatGPT 有實際呼叫連接器工具、Blender 出現一隻簡單的貓、檔案存入已設定的輸出資料夾。若沒有呼叫工具，先看桌面程式 **Status / 狀態** 各層，在 ChatGPT 的 App connector settings 按**一次 Refresh tools**，然後開**全新對話**重新選 App。通道停止時建立的舊對話可能一直顯示沒有工具。詳見[繁體中文連線恢復](CONNECTION_RECOVERY.zh-Hant.md)、[English recovery](CONNECTION_RECOVERY.md)及[ RC2 故障排解](TROUBLESHOOTING_RC2.md)。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
