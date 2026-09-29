# Changelog / 變更紀錄

## 2026-09-29 — tunnel recovery / 通道恢復

- A loaded tunnel with no running PID now tells the user to press Connect; Connect requests one launchd start. The 60-second abnormal-exit throttle and normal-exit preflight guard remain unchanged. / 已載入但沒有 PID 時明示按「一鍵連接」；Connect 只要求 launchd 啟動一次。異常退出的 60 秒節流及前置檢查正常退出規則不變。
- Added [connection recovery](docs/CONNECTION_RECOVERY.md), [繁中連線恢復](docs/CONNECTION_RECOVERY.zh-Hant.md), and the [incident record](docs/INCIDENT_20260929_TUNNEL_SESSION_TERMINATED.md). / 新增雙語恢復指南及事故紀錄。

## 2026-09-29 — documentation / 文件

- Added bilingual first-run walkthroughs, a README quick start, and a complete link map. / 新增雙語首次使用圖解、README 快速開始及完整連結地圖。
- Added documentation entry points for third-party components, validation and packaging limits. / 新增第三方元件、驗證與封裝限制的文件入口。
- This entry describes a **documentation-only** change. It does not assert a new product build or additional hardware testing. See [verification evidence](docs/VERIFICATION_EVIDENCE.md) for the observed scope. / 本項只記錄**文件改動**，不聲稱新增產品版本或實機測試；實測範圍見[驗證證據](docs/VERIFICATION_EVIDENCE.md)。
