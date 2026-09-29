# AI 代理快速安裝

此工具沒有 npm 套件。本機安裝可交給代理；帳戶端步驟仍須你親自完成。

## 一句交給代理

先執行 `git clone https://github.com/kingheiego/blender-web-bridge.git && cd blender-web-bridge`，再把這一行貼給在同一部 Mac 工作的 AI coding agent：

```text
Read AGENTS.md in this blender-web-bridge repo and follow it to install and verify Blender Web Bridge on this Mac. Stop and ask me only for the items under 'HUMAN ONLY'.
```

Codex 專用一行：

```text
Codex: Clone https://github.com/kingheiego/blender-web-bridge.git into a new directory on this Mac, read AGENTS.md, and follow it to install and verify Blender Web Bridge; leave only HUMAN ONLY steps to me.
```

Claude Code 專用一行：

```text
Claude Code: Clone https://github.com/kingheiego/blender-web-bridge.git into a new directory on this Mac, read AGENTS.md and CLAUDE.md, and follow them to install and verify Blender Web Bridge; leave only HUMAN ONLY steps to me.
```

| 代理負責 | 只有你負責 |
|---|---|
| 檢查 Mac、Blender、Python/Tk、迴環端口；安裝控制程式並報告實際寫入位置。 | 確認 ChatGPT 方案／工作空間／地區可使用 Secure MCP Tunnel 和自訂連接器。 |
| 指引 Setup；服務停止時準備固定版本元件。 | 在 OpenAI／ChatGPT 介面建立自己的 connector app、Tunnel 和 runtime key。 |
| 分別核對 Blender、通道程序與雲端輪詢；驗證真實唯讀網頁工具回覆。 | 在程式遮罩欄親自輸入 key；若 Blender 沒有回應，決定是否自行按 Connect（可能啟動受管理的 Blender）；按 Refresh tools；開全新對話；批准 ChatGPT 和 macOS 提示。 |

「30 秒測試」指一句快速發出的要求，不保證 30 秒內完成。先取得真實唯讀場景回覆，再送出：

> 幫我整個最簡單嘅測試：用一個立方體做隻簡單嘅貓出嚟，做完幫我存好。

> Run the simplest test: make a simple cat out of a cube, then save it for me.

恢復：先確認 Blender 有回應，再按 `Connect / 一鍵連接`。
在 ChatGPT 連接器設定按 `Refresh tools`。
開全新對話；參閱[連線恢復](CONNECTION_RECOVERY.zh-Hant.md)。

較長提示詞見[交給 AI 協助安裝](INSTALL_WITH_AI.md)。本工具與 OpenAI 無關，也未經 Apple 公證。
