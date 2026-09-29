# Connector icon: verified control boundary / 連接器圖示：已核實的控制邊界

## English

As of 2026-09-29, **Blender Showa House (Mac)** still shows ChatGPT's grey default icon. The public [1024 × 1024 PNG](../assets/icon.png) is available at `https://raw.githubusercontent.com/kingheiego/blender-web-bridge/main/assets/icon.png`. An available image is not evidence that ChatGPT has selected it.

### What sets the icon

- OpenAI's [plugin packaging documentation](https://developers.openai.com/plugins/build/plugins) says the package manifest's `extensions.com.openai.interface` controls OpenAI install-surface presentation. It defines `logo` and `composerIcon` as relative asset paths such as `./assets/logo.png`, not arbitrary fields on an MCP tool or a URL pasted into the app description. The [submission documentation](https://developers.openai.com/plugins/deploy/submission) separately lists a logo among the public listing details.
- The MCP [2025-11-25 schema](https://modelcontextprotocol.io/specification/2025-11-25/schema) permits `initialize.result.serverInfo.icons`. Each icon has required `src` and optional `mimeType`, `sizes` and `theme`; `src` can be an HTTP(S) or data URI, and `sizes` is an array such as `["1024x1024"]`. This advertises an icon that a supporting MCP client **can** display. The [2025-06-18 schema](https://modelcontextprotocol.io/specification/2025-06-18/schema) did **not** define `Implementation.icons`; attributing the field to that revision is incorrect.
- These are distinct paths. OpenAI's [remote MCP review documentation](https://developers.openai.com/plugins/deploy/app-review) lists the metadata imported by **Scan Tools**, including tools and server instructions, but does not say that ChatGPT imports `serverInfo.icons` as the plugin listing icon. We found no official OpenAI source establishing that changing `serverInfo.icons` updates this installed app's grey icon. The MCP allowance alone is insufficient to claim that behavior.

### What this repository controls

The installed Python `mcp` package is **1.30.0**. Its `mcp.types.Icon` has `src`, `mimeType` and `sizes`; `mcp.types.Implementation.icons` is optional; `mcp.server.fastmcp.FastMCP.__init__(icons=...)` passes icons to `mcp.server.lowlevel.Server`, and `mcp.server.session.ServerSession` emits them in `serverInfo`. The pinned `blender_mcp.server` constructs `FastMCP("BlenderMCP", ...)` without `icons`. Its current stdio initialization therefore reports `{"name":"BlenderMCP","version":"1.30.0"}` with no `icons`. Our `app/mcp_entry.py` could advertise icons without changing the 37 tools, but **that would prove only the MCP handshake, not ChatGPT's plugin icon**. We did not change product code or the live connector on an unverified assumption.

The current checkout has no `.codex-plugin/plugin.json`, root `plugin.json`, or OpenAI listing submission. The installed plugin shows version `1.0.0` (distinct from MCP server version `1.30.0`), developer `App developer`, website `Unavailable`, and the default icon. That version difference is further evidence that plugin listing metadata and MCP `serverInfo` are distinct, though it does not prove where the icon is stored. The inspected ChatGPT Manage screen allows name, description and tool refresh, while the inspected Platform tunnel editor allows name, description, organizations and ChatGPT workspaces. Neither exposes an icon field. The icon is **not controllable from this repository's current MCP entry point with a documented, verified ChatGPT effect**. We also cannot establish that the present plugin is editable only at creation time: the observed UI offers **Upload new version**, but its icon behavior has not been tested.

### Owner action and limits

1. If changing the **installed plugin**, download its ZIP and inspect its actual manifest. If it is a package using OpenAI's documented `extensions.com.openai.interface`, package the approved PNG under `./assets/` and set the applicable `logo` / `composerIcon` relative paths. Test that package independently. Then use **Upload new version** only if the owner chooses to change the installed plugin; inspect the rendered icon afterwards. The downloaded ZIP's format and whether this particular app accepts those fields remain unverified.
2. If instead creating a **public MCP plugin listing**, use the documented submission form's **Logo** listing field. This is a different publishing path and does not establish how to update the existing custom connector.
3. **Refresh tools** can refresh tool metadata, but there is no documented guarantee that it updates the listing icon. Re-adding the connector is likewise unverified and may create a different app. Neither action was taken. The Platform tunnel fields and ChatGPT's name/description fields cannot be used to enter the icon URL.

The repository commit only corrects this document. The ChatGPT icon is **not fixed or visually reverified**.

## 繁體中文

截至 2026-09-29，**Blender Showa House (Mac)** 在 ChatGPT 仍顯示灰色預設圖示。repo 已有[公開的 1024 × 1024 PNG](../assets/icon.png)，直連網址為 `https://raw.githubusercontent.com/kingheiego/blender-web-bridge/main/assets/icon.png`；圖片存在，不代表 ChatGPT 已採用。

### 已核實的設定途徑

- OpenAI 的[插件封裝文件](https://developers.openai.com/plugins/build/plugins)說明，安裝畫面的外觀由 package manifest 的 `extensions.com.openai.interface` 控制，其中 `logo` 和 `composerIcon` 使用 `./assets/logo.png` 一類的相對檔案路徑。[公開提交文件](https://developers.openai.com/plugins/deploy/submission)亦把 Logo 列為公開目錄資料。
- MCP 的 [2025-11-25 schema](https://modelcontextprotocol.io/specification/2025-11-25/schema)容許 `initialize.result.serverInfo.icons`：每項必須有 `src`，可另加 `mimeType`、`sizes`、`theme`；`src` 可用 HTTP(S) 或 data URI，`sizes` 可寫 `["1024x1024"]`。這只代表支援圖示的 MCP client **可以**顯示它。[2025-06-18 schema](https://modelcontextprotocol.io/specification/2025-06-18/schema)的 `Implementation` 並沒有 `icons`。
- 兩者不是同一設定。OpenAI 的[遠端 MCP 審核文件](https://developers.openai.com/plugins/deploy/app-review)列出 **Scan Tools** 會讀取的工具資料及 server instructions，沒有說 ChatGPT 會把 `serverInfo.icons` 當作插件清單圖示。我們找不到官方文件證實修改該欄會更改此 App 的灰色圖示。

### 這個 repo 能做到甚麼

現役 Python `mcp` 版本為 **1.30.0**。`mcp.types.Icon` 有 `src`、`mimeType`、`sizes`；`mcp.types.Implementation.icons` 可選；`FastMCP.__init__(icons=...)` 會傳到低層 `Server`，再由 `ServerSession` 放進 `serverInfo`。上游 `blender_mcp.server` 建立 `FastMCP("BlenderMCP", ...)` 時沒有設定 `icons`；目前 stdio 握手只回報 `{"name":"BlenderMCP","version":"1.30.0"}`，沒有 `icons`。`app/mcp_entry.py` 技術上可加這個欄位，並保留 37 個工具；但握手成功**不能證明** ChatGPT 插件圖示會改，所以本次沒有改產品程式碼或 live connector。

目前 repo 沒有 `.codex-plugin/plugin.json`、根目錄 `plugin.json` 或 OpenAI listing submission。已安裝插件顯示版本 `1.0.0`（與 MCP server 的 `1.30.0` 不同）、開發者 `App developer`、網站 `Unavailable` 及預設圖示。版本不同進一步顯示插件目錄資料與 MCP `serverInfo` 是兩套資料，但不能單憑這點確定圖示儲存位置。已檢查的 ChatGPT Manage 畫面只有名稱、描述和刷新工具；Platform tunnel 編輯畫面只有名稱、描述、組織和 ChatGPT workspace，均沒有圖示欄位。因此，**沒有已證實可由此 repo 的 MCP 入口控制該 ChatGPT 圖示的方法**。畫面有 **Upload new version**，故亦不能斷言圖示只可在建立時設定；該更新途徑仍未驗證。

### 擁有人可做的事及限制

1. 若要更改**現有插件**，先下載它的 ZIP，檢查真正的 manifest。如果它採用 OpenAI 文件所述的 `extensions.com.openai.interface`，把已批准的 PNG 放到 `./assets/`，並以相對路徑設定適用的 `logo`／`composerIcon`，先獨立測試。擁有人決定更新時才使用 **Upload new version**，然後在 ChatGPT 實際查看圖示。現有 ZIP 的格式、這個 App 是否接受上述欄位，仍未驗證。
2. 若是建立**公開 MCP 插件目錄項目**，使用官方提交表單的 **Logo** 欄位；這是另一條發佈途徑，不能推論它會更新目前的自訂連接器。
3. **Refresh tools** 可能更新工具資料，但沒有文件保證它會更新插件圖示。重新加入連接器亦未經驗證，可能產生另一個 App。本次沒有執行任何一項。不可把圖片網址填入 tunnel、App 名稱或描述欄位。

本次 commit 只修正文件；ChatGPT 圖示**尚未修好，亦沒有重新做畫面驗證**。
