# Third-party components / 第三方元件

Blender Web Bridge's controller source is under [MIT](../LICENSE). Blender, Python, `uv`, OpenAI `tunnel-client`, and `mcp-for-blender` are separate upstream projects with their own terms. This repo does not bundle Python, a tunnel-client binary, or credentials. The **exact** runtime versions, download URLs, and SHA-256 values used by **Prepare components** are in [`dependencies.lock.json`](../dependencies.lock.json); inspect the upstream distribution terms before redistributing any runtime component. / Blender Web Bridge 控制程式原始碼採用 [MIT](../LICENSE)。Blender、Python、`uv`、OpenAI `tunnel-client` 及 `mcp-for-blender` 是各自有授權條款的上游專案。repo 不附 Python、通道程式執行檔或憑證。**準備元件**所用的**確切**版本、下載網址及 SHA-256 見[`dependencies.lock.json`](../dependencies.lock.json)；重新分發任何執行元件前須查看上游條款。

Use the [link map](LINKS.md) for checked official Blender, Python and OpenAI pages. Component preparation verifies downloaded files against the lockfile; a checksum mismatch is a failure, not a prompt to skip verification. / 已核對的 Blender、Python、OpenAI 官方頁面見[連結地圖](LINKS.md)。準備元件時會依固定清單核對下載檔；雜湊不符代表失敗，不可略過驗證。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
