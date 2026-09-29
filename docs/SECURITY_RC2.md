# Security and public distribution / 安全與公開發佈

Public packaging is allowlist-only: runtime source, paired guides, dependency pins,
license and explicitly approved original images. It never recursively copies the
repository, user data, private handoff notes, logs, accounts, configuration,
credentials, model backups, runtime binaries or test output.
公開包只按白名單匯入，不遞迴複製 repository 或使用者資料。

`tools/build_public.py --output <path>` scans selected text, verifies exact asset
hashes and requires a human approval record for every image/icon. Any failure
prevents ZIP creation; an existing output file is never overwritten. The code
review package is not automatically a public package. All source scans are
heuristics, not a guarantee that arbitrary text contains no secret.
公開打包先檢查文字及每張圖的 hash 和人工批准；任何失敗都不建立 ZIP，亦不覆寫舊 ZIP。
文字掃描是啟發式檢查，不代表可證明任意內容完全沒有秘密。

The media gate requires a real person to inspect all visible pixels, metadata,
account chrome, personal paths, faces, tokens and source rights, then explicitly
record an approval of the exact hash. No code can prove that a checkbox corresponds
to an honest human review. The current [approval record](../RELEASE_IMAGE_REVIEW.json)
marks the included images/icon approved; any changed bytes need their own review.
圖片覆核須真正查看像素及 metadata、帳戶介面、私人路徑、人像、token 與來源權利，
再批准該 hash。程式不能證明人是否誠實完成查看；現有[批准紀錄](../RELEASE_IMAGE_REVIEW.json)
標記了本次圖片／圖示，若位元內容改變須重新覆核。

The new controller's export includes classification values only. It does not
export raw log messages. Existing local tunnel logs can contain request identifiers,
paths or account context and must remain private. Keys stay in Keychain or the
already explicitly approved legacy store; never in command arguments or source.
The tunnel receives the runtime key through its process environment, as before.

The loopback health opener ignores proxy environment variables for 127.0.0.1 only;
it does not change system proxy settings. All external network behavior remains
with the existing pinned client and explicitly requested dependency downloads.
No IP lookup, network interface enumeration, VPN command, route modification or
DNS configuration is added.

Lifecycle locks protect cooperating updater/controller processes, not a hostile
process with the same user privileges. Paths are checked for symlinks and special
files. The installer does not provide a filesystem sandbox for Blender tools.
Scene-preservation instructions are model guidance, not enforcement of all model
code. Inspect every model-changing action and do not automatically retry it.

MIT applies to the controller. Existing dependency versions and licenses remain
unchanged: OpenAI tunnel-client 0.0.15, uv 0.10.0, MCP for Blender 2.1.0 and its Python
dependencies. Binaries are not bundled. The Python transitive requirement versions
are pinned, but this work does not add a complete per-wheel hash lock; runtime
supply-chain verification beyond existing primary artifact hashes remains a gap.

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
