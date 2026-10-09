# 通道停止後如何恢復

若你在 ChatGPT 查詢 Blender 時看到 **「Session terminated」**，本機通道可能已停止。Blender 場景仍可能開著，內容沒有因此改動。系統顯示服務「已載入」，不代表它有正在運行的程序。

## 一鍵恢復

1. 在 Mac 開啟 **Blender Web Bridge**；若已開啟，進入 **Status / 狀態**。
2. 先自行開 Blender，等 MCP 插件有唯讀回應，再按 **Connect / 一鍵連接**。Connect 不會啟動 Blender。若通道仍未恢復，按 **Stop / 停止通道**，再次檢查後才按 **Connect**。Stop 只處理通道，不會關閉 Blender。
3. 按 **Check / 檢查**。確認 Blender 有回應、通道有正在運行的 PID（可在 `bridge.py status` 查看），並在必要 metrics 齊全時確認雲端層有新鮮的成功輪詢。單靠本機 `/readyz` 正常，不能證明 ChatGPT 已能使用工具。
4. 到 ChatGPT 中既有連接器的設定按 **Refresh tools**，開一個**新對話**，選擇該連接器，先問唯讀問題，例如「目前 Blender 場景叫甚麼名字？」。收到真正的工具回覆後，才繼續編輯。

如果舊對話是在通道中斷時建立，它可能仍保留當時空白或不可用的工具清單。**Refresh tools** 會更新連接器；**新對話**則載入目前的工具清單。在舊對話重問，仍可能得到「沒有工具」的答覆。

## Connect 仍無法恢復

熟悉 Mac 終端機的使用者可執行以下命令，只檢查本機通道服務。不要把憑證或私人 log 貼到公開問題。

```sh
launchctl list | grep -i blender
python3 "$HOME/Library/Application Support/BlenderWebBridge/app/bridge.py" status
```

在第一個結果找出你設定的通道 label；在第二個結果查看 `loaded`、`pid` 及 `detail`。若顯示已載入但沒有 PID，先回桌面程式按 **Connect**。必要時，把下方 `YOUR_TUNNEL_LABEL` 換成你自己設定的**確切 label**，再執行：

```sh
launchctl kickstart -k "gui/$(id -u)/YOUR_TUNNEL_LABEL"
```

如果找不到 label、狀態不明、前置條件失敗，或你不確定哪個服務屬於自己，請找人協助。不要猜測性重啟 Blender，也不要重建通道或金鑰。

## 這次修正了甚麼

較早版本可能在通道正常退出後，留下「服務已載入、程序已停止」的狀態。現時控制程式會明示**按 Connect**，而按鈕只要求啟動一次。異常退出仍有 60 秒節流；正常退出**不會**自動重啟，因為憑證或其他啟動前置條件失敗時也會正常退出，必須避免循環重啟。因此這是**一鍵恢復**，並非任何退出都會自動恢復。

另見 [2026-09-29 事故紀錄](INCIDENT_20260929_TUNNEL_SESSION_TERMINATED.md)及[英文指南](CONNECTION_RECOVERY.md)。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
