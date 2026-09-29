# Network recovery contract / 網絡恢復契約

## Ownership / 分工

launchd is the only process supervisor. `bridge.py daemon` takes one inherited lock
and execs the existing pinned tunnel-client once. It does not contain a restart loop.
The UI polls local health only. It neither discovers nor pins the public IP.
launchd 是唯一程序監督者；daemon 持有鎖後直接 exec 固定版本客戶端，不增加重啟迴圈。
UI 只觀察本機狀態，不偵測或固定公網 IP。

Primary-source review: tunnel-client v0.0.15,
`pkg/controlplane/internal/poller.go` (blob `f5068e06d758369a2f9f20e842d2d54cc86ca463`) and
`pkg/controlplane/internal/metrics.go` (blob `47f4dafaa2ac0d9c9d65d0c3d7380887feb93971`).
The existing poller uses exponential backoff (200 ms minimum, 10 s maximum), jitter,
and Retry-After handling. Successful polling resets that backoff. These are source
observations, not a new hardware/VPN experiment. Source:
https://github.com/openai/tunnel-client/blob/v0.0.15/pkg/controlplane/internal/poller.go

The LaunchAgent retries unsuccessful process exits with a 60-second throttle.
Successful exit, missing credentials or an explicit Stop does not create a restart
storm under the new policy. Loaded legacy agents must be stopped before deployment;
unknown or differently bound agents are refused, not overwritten.
LaunchAgent 對異常程序退出作 60 秒節流；正常退出、憑證前置檢查失敗或手動停止不形成重啟風暴。
舊 agent 必須先停止再部署；不明或不同綁定的 agent 只會拒絕更改。

## Evidence / 證據

`/readyz` and current PID/generation prove the local process only. Cloud status
requires both valid last-success and error-counter metric families. Counters are
partitioned by `error_kind`; partitions are checked rather than blindly summed
across unrelated clients. Zero is not invented when an instrument is absent.
The upstream exporter may omit an unused zero-error series: rc2 then stays unknown.
This conservative choice can keep an actually working connection from showing
cloud-green until enough metrics exist. It is not proof the connection is broken.

同一採樣同時見到成功與錯誤增加，無法得知先後，因此維持未知；之後沒有新增錯誤、成功時間
明確前進，才可恢復。未來時間戳不容忍為成功，非有限值、負值、重複系列、缺值一律未知。
成功證據最多有效 90 秒；觀察中斷會撤銷正常，但保留已知錯誤及計數器歷史，避免舊成功被重新接納。

Structured log diagnostics are bounded and generation-scoped. Only an actual
fresh poll-failure event with status 403 and code
`unsupported_country_region_territory` is classified as region rejection. Generic
403 means authorization rejection; it does not imply a country diagnosis. Missing
metrics remain unknown even when a separate region diagnostic is available.
明確的地區拒絕會單獨提示；不把任意含 403 的文字當成地區封鎖，也不把診斷取代完整 metrics。

The upstream poller still retries its own polls, including policy errors. rc2 does
not patch that binary or claim retries stop. It does not restart the process to
repair a policy rejection. No tunnel/key recreation or network switching occurs.

## Non-replay boundary / 不重播邊界

The lifecycle RPC entry accepts only `get_scene_info`, never `execute_code`.
Polling retries are not a user-model-operation retry queue. A timed-out modeling
operation has an unknown outcome: inspect the actual scene and saved files before
any separately approved retry. The upstream MCP/model execution path is not
claimed to have newly proven exactly-once semantics.
連接管理不會重播建模；建模逾時不能當作未執行，亦不聲稱上游工具已證明 exactly-once。

## Compatibility limits / 相容性界線

No fixed IP is required by this controller. That does not guarantee every changing
VPN exit is supported by the service. Account, workspace and region restrictions
remain external. Do not alter VPN/Tailscale/routes/DNS/proxy to run these tests.
Observe naturally occurring outages and recovery only within separately approved
local acceptance. Do not use restart loops to evade region policy.
Official region information (checked 2026-09-29):
https://help.openai.com/en/articles/7947663-chatgpt-supported-countries
