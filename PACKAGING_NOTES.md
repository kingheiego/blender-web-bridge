# Packaging notes / 封裝說明

This repository is a **source package** with `Install.command` and `install.py`. Installation writes local files and a Desktop `.app` but does **not** start services or download runtime components. The app's first-time **Prepare components** action downloads pinned, SHA-256-verified components listed in [`dependencies.lock.json`](dependencies.lock.json). Python 3.10+ with Tk is a separate prerequisite; Python is **not bundled**. The app is **not notarized**. / 此 repo 是含 `Install.command` 及 `install.py` 的**原始碼包**。安裝只寫入本機檔案及桌面 `.app`，**不**啟動服務或下載執行元件。首次由 App 的**準備元件**下載並核對 [`dependencies.lock.json`](dependencies.lock.json) 所列固定版本與 SHA-256。Python 3.10 或以上及 Tk 須另外安裝；**不附 Python**。App **未經 Apple 公證**。

Save and close Blender and stop the tunnel before Prepare components. That action also backs up the regular Blender add-on and preferences, then installs and enables the pinned add-on there. The installed controller never creates a Blender auto-restart LaunchAgent; the user opens and closes Blender normally. Existing users may retire only a recognized legacy Blender auto-restart service from Setup after saving the scene. / 準備元件前先儲存並關閉 Blender、停止通道；此步亦會備份日常 Blender 插件與偏好，然後安裝並啟用固定版本插件。控制程式不建立令 Blender 自動重開的 LaunchAgent；使用者自行開關 Blender。舊用戶儲存場景後，可在設定頁停用已核實的舊版自動重開服務。

The installer copies a fixed set of app files and selected guide assets into the installed support folder; the complete, current guides and link map live in this GitHub repository. For the supported first-run path, begin at [README](README.md) or [Getting started / 入門指南](docs/GETTING_STARTED.md). / 安裝器只複製固定清單的程式與部分指南素材到本機支援資料夾；完整的最新指南和連結地圖以本 GitHub repo 為準。首次使用請由 [README](README.md) 或[入門指南](docs/GETTING_STARTED.zh-Hant.md)開始。

The macOS bundle keeps its stable `Blender Web Bridge.app` filename and identifier; its visible display name and window title are **Blender Web Bridge / Blender 網頁橋接器**. / macOS bundle 檔名與識別字維持不變，App 顯示名稱與視窗標題則使用完整中英文。

This package is provided for **MacBook (macOS) only**. Windows packaging, setup and functional verification are left to Windows users who choose to port the source. / 此封裝只提供俾 **MacBook（macOS）** 使用；Windows 的封裝、設定與功能驗證由自行移植的使用者負責。

`PUBLIC_SOURCE_SHA256.json` records the minimal allowlisted source ZIP, not every historical guide or showcase file in the GitHub checkout. / `PUBLIC_SOURCE_SHA256.json` 核對的是最小白名單原始碼 ZIP，不涵蓋 GitHub checkout 內每份歷史指南或展示檔。
