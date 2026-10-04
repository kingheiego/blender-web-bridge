# Changelog / 變更紀錄

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
