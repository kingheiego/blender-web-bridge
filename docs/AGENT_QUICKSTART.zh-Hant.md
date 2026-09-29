# AI 代理快速安裝

此工具沒有 npm 套件。本機安裝可交代理協助，但帳戶端步驟仍須你親自完成；這不是一鍵全自動安裝。

## 一句交給代理

即使尚未 clone repo，也可把以下同一行貼給在自己 Mac 上工作的 Codex 或 Claude Code：

```text
On my Mac, clone https://github.com/kingheiego/blender-web-bridge.git into a new directory (or use an existing checkout without overwriting it), read AGENTS.md and CLAUDE.md if you are Claude Code, then follow them to install and verify Blender Web Bridge. Stop and ask me only for HUMAN ONLY steps.
```

| 代理負責 | 只有你負責 |
|---|---|
| 檢查 Mac、Blender、Python/Tk、迴環端口；安裝控制程式並報告實際寫入位置。 | 確認 ChatGPT 方案／工作空間／地區資格、開發者模式、Platform 通道權限及工作空間關聯；欠權限時請管理員處理。 |
| 指引 Setup；服務停止時準備固定版本元件。 | 在 OpenAI／ChatGPT 介面建立自己的 connector app、Tunnel 和 runtime key。 |
| 分別核對 Blender、通道程序與雲端輪詢；驗證真實唯讀網頁工具回覆。 | 在程式遮罩欄親自輸入 key；若 Blender 沒有回應，決定是否自行按 Connect（可能啟動受管理的 Blender）；按 Refresh tools；開全新對話；批准 ChatGPT 和 macOS 提示。 |

「30 秒測試」指一句快速發出的要求，不保證 30 秒內完成。先取得真實唯讀場景回覆，再送出：

> 幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。

> Run the simplest test: make a simple cat out of a cube, then save it for me.

恢復：先檢查 Blender，再按 `Connect / 一鍵連接`。若 Blender 無回應，只有你可決定是否按；Connect 可能啟動受管理的 Blender。
在 ChatGPT 連接器設定按 `Refresh tools`。
開全新對話；參閱[連線恢復](CONNECTION_RECOVERY.zh-Hant.md)。

較長提示詞見[交給 AI 協助安裝](INSTALL_WITH_AI.md)。本工具與 OpenAI 無關，也未經 Apple 公證。
