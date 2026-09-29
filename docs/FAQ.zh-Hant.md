# 常見問題

[English](FAQ.md) · [入門指南](GETTING_STARTED.zh-Hant.md) · [安全細節](SECURITY_RC2.md)

## 使用這個工具，OpenAI／ChatGPT 會封鎖我的帳戶嗎？

本工具使用 OpenAI 支援的 [Secure MCP Tunnel 與自訂連接器開發功能](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)。它不是破解或 jailbreak，也不會繞過收費或存取權限。使用有文件記載的開發功能，本身不等於違規。不過，自訂 App 可能顯示 **dev mode／DEVELOPMENT** 審核狀態；通道是否可用，取決於你的方案、工作空間及地區；你亦須為容許它執行的程式碼負責。我們不能保證 OpenAI 日後政策不變。本專案與 OpenAI 沒有從屬關係，也沒有獲得其認可。

## 為何不用 Codex 算力或 token，仍能控制我的 Mac？

模型在你正常 ChatGPT 對話中於 OpenAI 伺服器運行。通道只負責傳送要求；**你的 Mac** 上的本機 MCP server 才實際執行 Blender 呼叫。這條流程不使用 Codex token 或 Codex runtime。工作期間，Mac 必須保持喚醒及連線。

## 真正的風險是甚麼？

- `execute_blender_code` 在**你的 Blender 程序內執行任意 Python**。這正是功能所在，也代表錯誤呼叫可能改壞或遺失作品。
- 上游可選的 **Safe Mode** 在本控制程式的 runtime 中啟用，會在模型程式碼路徑阻擋 `os`、`sys`、`subprocess`、`socket` 等匯入和危險的直譯器逃逸方式。它是防護規則，**不是包住 Blender 的沙盒**；不可因此放心執行不可信程式碼。
- Blender 的本機 loopback socket **沒有驗證**；Mac 上任何本機程序都可能呼叫它。它只應綁定 loopback，**絕不能暴露到網絡**。
- 模型讀到的素材名稱或描述，可能含有企圖誘導危險程式碼的 **prompt injection**。Safe Mode 會降低這條風險，但不能保證完全消除。
- 你要求 ChatGPT 查看的場景資料、視窗截圖及路徑，可能會傳到 ChatGPT。不要請它查看不想分享的私人內容。
- runtime API key 存在 **macOS Keychain**，不在此 repo；不要放進提示詞、公開 issue 或截圖。
- App **未經 Apple 公證**，首次執行時 macOS 可能警告；只開啟你信任的副本。
- 留意 **Blender 未儲存的工作**。建模期間不要按 **Prepare components／準備元件**；控制程式可能拒絕操作，而不會替你停止正在運行的服務。高風險操作前先儲存並檢查場景。

## 哪些情況尚未測試？

已記錄的範圍是 Apple 晶片 macOS、Python 3.10 或以上及 Tk。**未測試** Intel Mac、完整整機重啟、長時間連續運行、真實 VPN 出口 IP 輪換、公證，以及所有 ChatGPT 方案、地區或工作空間。控制程式**不需固定公網 IP**，亦**不更改 VPN、路由、DNS、Tailscale 或 proxy**；但不能保證某個 VPN 出口會獲服務接受。見[驗證證據](VERIFICATION_EVIDENCE.md)。

## 每位使用者要在自己的 Mac 檢查或調整甚麼？

| 檢查項目 | 在哪裏設定或核對 |
|---|---|
| **Python 3.10 或以上並有 Tk**；建議 3.11 或以上 | 另外安裝，然後在 repo 資料夾執行 `./Install.command --check`。此工具不附 Python。 |
| 自己的 `Blender.app` 位置 | 桌面程式 **Setup／設定 → Blender.app**。 |
| 未被佔用的 loopback 連接埠 | 預設 **9876**。服務停止時，在你自己的 `~/Library/Application Support/BlenderWebBridge/` 目錄中檢查或更改 `config.json` 的 `port`；桌面設定頁沒有連接埠欄位。只可綁定 loopback。 |
| 自己的 Tunnel ID 和 runtime API key | 首次使用 **Setup／設定** 欄位；金鑰只貼在遮罩欄。此 rc2 控制程式不支援替換既有身份／金鑰。 |
| 模型輸出資料夾 | **Setup／設定 → Output folder／輸出資料夾**；填 Mac 上可寫入的完整路徑。 |
| Mac 保持喚醒和連線 | 長時間工作前，檢查 macOS 電源／睡眠設定及網絡。 |

每位使用者都要有自己的合資格 ChatGPT 設定、通道、金鑰及本機路徑；別人的可用設定不會自動搬到你的 Mac。

## 可以一直開着通道嗎？

Blender socket 只在 loopback 監聽，通道則**向外**連接 OpenAI。這限制網絡暴露，但不能保證本機程序或錯誤工具呼叫沒有風險。**Stop／停止通道**只停止通道，Blender 仍保持開啟；**只關閉桌面面板不會斷線**。不需要 ChatGPT 存取時請停止通道，並照常儲存 Blender 作品。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter
