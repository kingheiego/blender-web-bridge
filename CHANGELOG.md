# Changelog / 變更紀錄

## 2.0.2-rc3 · 2026-10-09

- OpenAI `tunnel-client` 固定至 0.0.16，`uv` 固定至 0.12.24；MacBook（macOS）下載檔按官方 SHA-256 驗證。
- 下載快取改用版本及架構命名，升級時不會誤把舊版 `uv.tar.gz` 或 `tunnel-client.zip` 當成新版。
- 保留手動開關 Blender、MacBook 專用範圍和既有通道身份；相容及現用連線結果以本版驗收紀錄為準。
- Mac 已實測 0.0.16 通道：關閉 Blender 不自動重開，手動重開後同一條 ChatGPT 連線真實讀到場景；測試後將 Blender 留在關閉狀態。

## 2.0.2-rc2 · 2026-10-09

- 面板視窗、頁首和 macOS App 顯示名稱改為完整中英文：`Blender Web Bridge / Blender 網頁橋接器`；測試畫面名稱亦不再使用 `BWB／UI／QA` 簡寫。維持既有 bundle 路徑及通道身份，避免令舊版升級失效。
- 產品支援範圍明確限定為 MacBook（macOS）；Windows 由使用者自行移植與驗證，不列作本產品的待辦或完成條件。

## 2.0.2-rc1 · 2026-10-09

- 改為使用者自行開啟日常 Blender；Connect 只連通道，不建立或重啟 Blender 的 LaunchAgent。
- 舊版升級可在設定頁確認停用已核實的自動重開服務；先備份服務檔，只在儲存場景及停止通道後關閉舊受管理實例。
- Prepare components 在 Blender 關閉後備份日常偏好與插件，安裝並啟用固定版本 MCP 插件；現有 Blender 或通道仍運行時拒絕更新。
- `mcp-for-blender` 固定至 2.1.9、插件 1.8／協定 13；升級後需在 ChatGPT 刷新工具清單。
- Mac 實際完成「關閉不重開 → 手動重開 → 同一條 ChatGPT 通道再讀場景」；Windows 插件載入及偏好 readback 通過，GUI socket 尚未實測。207 項來源測試中 205 通過、2 項既有略過。

## 2.0.1-rc3 · 2026-10-04

- 修正下載 `.partial` 硬連結可能改動其他檔案的問題；使用獨立暫存檔且不覆蓋中途出現的目的檔。
- 在建立 runtime／state 子目錄前完成符號連結檢查，保留既有目錄權限。
- 補強 opt-in 舊式憑證檔的路徑、類型、擁有者、連結數、權限與大小檢查。
- 元件雜湊狀態明列主要下載物範圍，統一驗收文件。
- 新增 15 項回歸；完整來源 202 項中 200 通過、2 因缺少第二個檔案系統略過。
- Mac 隔離下載、安裝升級及精確還原成功；新 MCP 環境完成兩次真實本機唯讀場景查詢。


## 2026-09-29 — tunnel recovery / 通道恢復

- A loaded tunnel with no running PID now tells the user to press Connect; Connect requests one launchd start. The 60-second abnormal-exit throttle and normal-exit preflight guard remain unchanged. / 已載入但沒有 PID 時明示按「一鍵連接」；Connect 只要求 launchd 啟動一次。異常退出的 60 秒節流及前置檢查正常退出規則不變。
- Added [connection recovery](docs/CONNECTION_RECOVERY.md), [繁中連線恢復](docs/CONNECTION_RECOVERY.zh-Hant.md), and the [incident record](docs/INCIDENT_20260929_TUNNEL_SESSION_TERMINATED.md). / 新增雙語恢復指南及事故紀錄。

## 2026-09-29 — documentation / 文件

- Added bilingual first-run walkthroughs, a README quick start, and a complete link map. / 新增雙語首次使用圖解、README 快速開始及完整連結地圖。
- Added documentation entry points for third-party components, validation and packaging limits. / 新增第三方元件、驗證與封裝限制的文件入口。
- This entry describes a **documentation-only** change. It does not assert a new product build or additional hardware testing. See [verification evidence](docs/VERIFICATION_EVIDENCE.md) for the observed scope. / 本項只記錄**文件改動**，不聲稱新增產品版本或實機測試；實測範圍見[驗證證據](docs/VERIFICATION_EVIDENCE.md)。
