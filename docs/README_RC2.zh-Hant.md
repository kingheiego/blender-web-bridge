# Blender Web Bridge 使用說明

現行 GitHub 入口是[根目錄 README](../README.md)；此獨立說明仍由本機安裝器複製，
故保留離線可讀的操作重點。完整步驟見[英文入門指南](GETTING_STARTED.md) ·
[繁體中文入門指南](GETTING_STARTED.zh-Hant.md) · [所有連結](LINKS.md)。

**一句交給 Mac 上的 AI 代理：**

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

本版是 **2.0.1-rc2 程式候選版**，不是已完成 Mac 實機驗收的發佈版。

解壓後先看 [首次設定圖解](SETUP_RC2.html)，再雙擊 `Install.command`。需要自行安裝 Blender、
Python 3.10 或以上及 Tk，建議 3.11 或以上；MCP 另用固定 Python 3.11 環境。
安裝不會啟動或停止服務，也不修改 VPN、Tailscale、路由、DNS、proxy 或既有帳戶身份。

更新時請先停止通道、關閉面板；**不用關閉 Blender**。本版安裝器同時鎖定 UI、控制流程及
通道程序，逐目標暫存，再以交易紀錄還原。還原失敗會拒絕繼續更新，不會假報成功。

首次使用在設定頁提供自己的既有通道資料。已存在的身份與金鑰保持不變，留空不代表刪除。
「準備元件」只供兩個專用服務均未啟動時使用；服務仍在運行會拒絕，而不是替你關閉 Blender。
已有元件的現用安裝不需要再次下載元件。

完整安裝不是一鍵全自動。本人須確認 ChatGPT 資格、開發者模式、Platform 通道權限與工作空間關聯，
建立 App、通道及金鑰，在遮罩欄親自輸入金鑰，批准 ChatGPT／macOS 提示、刷新工具並開新對話選連接器。端口不可用時，
Connect 可能啟動受管理的 Blender。一鍵連接後有四層：Blender 本機回覆、通道程序、雲端 poll 證據、ChatGPT 網頁工具結果。
`/readyz` 不代表雲端正常；metrics 缺少、異常或過期均顯示未知。持續收到明確地區 403 時
會顯示原因，但不重啟通道、不換 API key、不切換出口。

網頁驗收必須先在 ChatGPT 收到兩次真實唯讀工具回覆，再自行在面板記錄；這不是工具
自動驗證你的帳戶。紀錄最多維持五分鐘，只在同一面板觀察期間及同一程序有效。
曾觀察到斷線後，必須重新驗收，不能因網絡恢復而自動沿用舊的通過紀錄。

停止通道會保留 Blender 和未儲存模型，下次登入仍維持停止。關閉面板則不會停止既有連線。
登入自動啟動與程序意外退出由同一個 launchd agent 管理；客戶端負責網絡 poll 退避重試。
通道停止或舊對話沒有工具時，先檢查 Blender；有唯讀回應後才按 Connect，否則由本人決定是否按。
然後在連接器設定刷新工具、開新對話選連接器，核對真正的唯讀工具回覆。

三個案例均是歷史案例，不能當作 rc2 重測。另有 [2026-09-29 有限網頁實測](VERIFICATION_EVIDENCE.md)，
包括唯讀查詢及當時開啟的預設場景另存副本；這不等於完整 Mac 實機驗收。只有一句話案例保存了原始提示詞；
另兩個詳細案例明確標示原文未保存。見 [案例](EXAMPLES_RC2.md) 及 [歷史驗收清單](ACCEPTANCE.md)。

九個發佈圖檔／圖示均已在本樹中，雜湊相符並獲准公開發佈；另有兩張網頁證據截圖
僅遮蓋本機路徑中的使用者名稱，其他像素未改動，詳見[驗證證據](VERIFICATION_EVIDENCE.md)。
`tools/build_public.py` 仍會檢查發佈圖片審批。
詳見根目錄 `README_RC2.md` 及 `release-assets.json`。不保證所有 VPN 出口、Mac、帳戶均支援。
