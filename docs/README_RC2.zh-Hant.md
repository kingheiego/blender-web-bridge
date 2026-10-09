# Blender Web Bridge／Blender 網頁橋接器 使用說明

Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)

現行 GitHub 入口是[根目錄 README](../README.md)；此獨立說明仍由本機安裝器複製，
故保留離線可讀的操作重點。完整步驟見[英文入門指南](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/GETTING_STARTED.md) ·
[繁體中文入門指南](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/GETTING_STARTED.zh-Hant.md) · [所有連結](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/LINKS.md)。

**一句交給 Mac 上的 AI 代理：**

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

本版是 **2.0.2-rc2 程式候選版**；面板及 App 的可見名稱均使用完整中英文。本頁歷史驗收紀錄屬舊版本，實機驗收另以本次部署結果為準。

解壓後先看 [首次設定圖解](SETUP_RC2.html)，再雙擊 `Install.command`。需要自行安裝 Blender、
Python 3.10 或以上及 Tk，建議 3.11 或以上；MCP 另用固定 Python 3.11 環境。
安裝不會啟動或停止服務，也不修改 VPN、Tailscale、路由、DNS、proxy 或既有帳戶身份。

更新時請先停止通道、關閉面板；**不用關閉 Blender**。本版安裝器同時鎖定 UI、控制流程及
通道程序，逐目標暫存，再以交易紀錄還原。還原失敗會拒絕繼續更新，不會假報成功。

首次使用在設定頁提供自己的既有通道資料。已存在的身份與金鑰保持不變，留空不代表刪除。
「準備元件」前先儲存並關閉 Blender，再停止通道。此步會核對固定版本下載、
為日常 Blender 的插件及偏好建立回復副本，並將 MCP 插件安裝及啟用；
Blender 或通道仍在運行時會拒絕，不會替你強行關閉。
啟用插件的「Auto-Start Server」後，每次自行開 Blender 都會提供本機 socket，
關閉 Blender 則停止，不會自動重開。

若從會自動重開 Blender 的舊版升級，先儲存場景並停止通道；到設定頁按
「停用舊版 Blender 自動重開」，確認後它只會備份及停止已核實的舊服務。
待舊實例關閉，再執行「準備元件」。

完整安裝不是一鍵全自動。本人須確認 ChatGPT 資格、開發者模式、Platform 通道權限與工作空間關聯，
建立 App、通道及金鑰，在遮罩欄親自輸入金鑰，批准 ChatGPT／macOS 提示、刷新工具並開新對話選連接器。
先自行開啟 Blender；MCP 插件會啟動本機 socket，之後才按 Connect。Connect 不會自行啟動 Blender，關閉 Blender 後亦不會自動重開。一鍵連接後有四層：Blender 本機回覆、通道程序、雲端 poll 證據、ChatGPT 網頁工具結果。
`/readyz` 不代表雲端正常；metrics 缺少、異常或過期均顯示未知。持續收到明確地區 403 時
會顯示原因，但不重啟通道、不換 API key、不切換出口。

網頁驗收必須先在 ChatGPT 收到兩次真實唯讀工具回覆，再自行在面板記錄；這不是工具
自動驗證你的帳戶。紀錄最多維持五分鐘，只在同一面板觀察期間及同一程序有效。
曾觀察到斷線後，必須重新驗收，不能因網絡恢復而自動沿用舊的通過紀錄。

停止通道會保留 Blender 和未儲存模型，下次登入仍維持停止。關閉面板則不會停止既有連線。
登入自動啟動與程序意外退出由同一個 launchd agent 管理；客戶端負責網絡 poll 退避重試。
通道停止或舊對話沒有工具時，先檢查 Blender；有唯讀回應後才按 Connect，否則由本人決定是否按。
然後在連接器設定刷新工具、開新對話選連接器，核對真正的唯讀工具回覆。

三個案例均是歷史案例，不能當作 rc2 重測。另有 [2026-09-29 有限網頁實測](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/VERIFICATION_EVIDENCE.md)，
包括唯讀查詢及當時開啟的預設場景另存副本；這不等於完整 Mac 實機驗收。只有一句話案例保存了原始提示詞；
另兩個詳細案例明確標示原文未保存。見 [案例](EXAMPLES_RC2.md) 及 [歷史驗收清單](ACCEPTANCE.md)。

九個發佈圖檔／圖示均已在本樹中，雜湊相符並獲准公開發佈；另有兩張網頁證據截圖
僅遮蓋本機路徑中的使用者名稱，其他像素未改動，詳見[驗證證據](https://github.com/kingheiego/blender-web-bridge/blob/main/docs/VERIFICATION_EVIDENCE.md)。
`tools/build_public.py` 仍會檢查發佈圖片審批。
詳見根目錄 `README_RC2.md` 及 `release-assets.json`。不保證所有 VPN 出口、Mac、帳戶均支援。

Author / 作者: @kinghei.ego/@ai.alter (GitHub: kingheiego)

本版改為手動開關日常 Blender，固定 MCP 2.1.9。完整來源測試 207 項（205 通過、2 項既有略過）；Mac 已做真實 ChatGPT 工具查詢及關閉／重開驗證，公開來源已做全新安裝、升級與 rollback 測試。範圍與未測項目見[驗收狀態](ACCEPTANCE.md)。固定檔名中的 RC2 保留以相容現有安裝器。
