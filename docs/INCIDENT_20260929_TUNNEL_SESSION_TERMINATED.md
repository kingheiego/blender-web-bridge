# 2026-09-29 tunnel incident: “Session terminated” / 通道事故紀錄

## Symptom and cause / 症狀與原因

On 2026-09-29 (Hong Kong time), a ChatGPT `get_scene_info` request returned **“Session terminated.”** The owner found that the tunnel LaunchAgent was loaded but had no running PID. The local log recorded a clean stop at **21:21:23**. The owner manually pressed **Connect**, which restored the tunnel with PID **4559**, `/readyz` HTTP 200, and a fresh poll. These initial incident observations were reported by the owner; the private log and ChatGPT conversation are not published here.

The 2.0.0 service policy used `KeepAlive=true`. The 2.0.1-rc2 candidate wrote `KeepAlive={SuccessfulExit:false}` with `ThrottleInterval=60`. The latter restarts abnormal exits but leaves a cleanly exited service loaded without a process. A startup prerequisite failure also returns normal exit intentionally, so changing back to unconditional `KeepAlive=true` would retry that failure every 60 seconds. The actual clean-exit trigger in this incident remains **UNKNOWN**.

2026-09-29（香港時間），ChatGPT 呼叫 `get_scene_info` 時回報 **「Session terminated」**。擁有人發現通道 LaunchAgent 已載入，卻沒有運行中的 PID；本機 log 記錄 **21:21:23** 正常停止。擁有人手動按 **Connect** 後，通道以 PID **4559** 恢復，`/readyz` 回 HTTP 200，並出現新鮮輪詢。這些初始事故資料由擁有人提供；私人 log 與 ChatGPT 對話不在此公開。

2.0.0 的服務策略是 `KeepAlive=true`；2.0.1-rc2 候選版改成 `KeepAlive={SuccessfulExit:false}`，另設 `ThrottleInterval=60`。後者會重啟異常退出，但正常退出後可能只剩「已載入、無程序」。啟動前置條件失敗亦刻意以正常狀態退出，因此直接改回無條件 `KeepAlive=true` 會每 60 秒重試該失敗。這次正常退出的直接觸發原因仍是 **未知**。

## Recovery evidence / 恢復證據

At **22:00:40–22:00:41**, the supported `disconnect` path stopped only the tunnel. At **22:00:55–22:00:56**, the supported `connect` path requested one start. At **22:01:11**, `launchctl list` showed the tunnel running with new PID **14543**, while the Blender service remained running. A local read-only scene check returned `Yellow_Train_Platform` with **4,340 objects**, and `/readyz` returned HTTP 200. The `commands_poll_last_successful_timestamp_seconds` metric corresponded to **22:01:28 HKT**, observed at **22:01:31 HKT**. A separate read-only connector call confirmed **47 materials**. The owner reported no lost work; the contents of unsaved work were not independently audited. No modeling or save command was run.

The controller's cloud layer still showed `unknown` because a required error-counter metric was absent or ambiguous. The read-only connector call succeeded, but a new **ChatGPT web conversation's** tool reply was **not independently verified** in this follow-up. A ready local process and fresh poll do not by themselves prove web acceptance.

於 **22:00:40–22:00:41**，產品的 `disconnect` 路徑只停止通道；**22:00:55–22:00:56**，`connect` 要求啟動一次。**22:01:11**，`launchctl list` 顯示新 PID **14543**，Blender 服務仍在運行。唯讀場景檢查回報 `Yellow_Train_Platform`、**4,340 個物件**；`/readyz` 回 HTTP 200。`commands_poll_last_successful_timestamp_seconds` 對應 **22:01:28（香港時間）**，於 **22:01:31** 觀察到。另一次唯讀連接器呼叫確認 **47 種材質**。擁有人回報沒有工作損失；未儲存工作的內容未經獨立審計，也沒有執行建模或儲存指令。

控制程式的雲端層仍顯示 `unknown`，因必要的錯誤計數 metric 缺席或不明；唯讀連接器呼叫成功，但本次後續檢查**沒有獨立核實**新 **ChatGPT 網頁對話**的實際工具回覆。本機程序就緒和新鮮輪詢本身不等於網頁驗收成功。

## Fix and lesson / 修正與教訓

The controller now says **“Loaded, no running PID; press Connect to restart.”** Its existing Connect path starts that loaded service once. The LaunchAgent policy and 60-second throttle remain unchanged, preserving normal exit on prerequisite failure without a restart loop. Recovery from a clean exit requires a user click; automatic clean-exit recovery is **not** claimed. The [English](CONNECTION_RECOVERY.md) and [繁體中文](CONNECTION_RECOVERY.zh-Hant.md) guides explain that click and the new-conversation tool refresh.

控制程式現時會顯示**「服務已載入但沒有程序；按『一鍵連接』重新啟動」**，既有 Connect 路徑會要求該服務啟動一次。LaunchAgent 規則和 60 秒節流不變，保留前置條件失敗時正常退出、不循環重啟的特性。正常退出後仍**需要使用者按一次**；本次不聲稱已實現自動恢復。詳見[英文](CONNECTION_RECOVERY.md)及[繁體中文](CONNECTION_RECOVERY.zh-Hant.md)恢復指南。
