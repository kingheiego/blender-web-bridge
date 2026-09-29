# Troubleshooting / 故障排解

| Observation / 現象 | Meaning and safe action / 意義及安全處理 |
|---|---|
| Local ready, cloud unknown / 本機就緒、雲端未知 | Missing, stale or ambiguous evidence. Wait for a fresh check; do not declare web usable. / 等新鮮採樣，不可假報網頁可用。 |
| A recent success then a new error / 成功後再失敗 | Normal status is revoked; an unambiguous newer success is required. / 撤銷正常，等明確較新成功。 |
| `403 unsupported_country_region_territory` | Service region-policy rejection, not a dead Blender. Check official eligibility or contact support. Do not switch network, recreate identity or repeatedly restart. / 地區政策拒絕，不代表 Blender 死機；核對官方資格，不切換網絡或重建身份。 |
| Generic 401/403 / 一般 401 或 403 | Authorization rejected; not enough evidence to call it a region problem. Preserve the existing key and inspect configuration locally. / 不能推斷為地區問題，保留既有金鑰。 |
| Blender uncertain or busy / Blender 忙碌或未確認 | No valid read-only response. Let rendering finish or inspect Blender locally; rc2 does not restart it. / 等渲染完成或本機檢查，不強制重啟。 |
| Network resumes but web stays unknown / 恢復後網頁仍未知 | Expected: repeat read-only web acceptance. Old pass records cannot revive. / 正常設計，重新做唯讀網頁驗收。 |
| Installer locked / 更新鎖被持有 | Close the panel and stop only the tunnel. Do not delete lock files. / 關面板並停止通道，不刪鎖檔。 |
| `rollback_incomplete` | Keep all `.bwb-*` directories and the journal. Use the reviewed explicit rollback while stopped; do not start the candidate. / 保留交易紀錄及所有備份，明確還原，勿啟動候選版。 |
| Existing profile differs / 舊 profile 不同 | Fail-closed. Codex must compare ID, key binding, executable, health address and JSON log format without regenerating identity. / 拒絕自動遷移，人工比對，不重建身份。 |
| Symlink refused / 符號連結遭拒 | Use a genuine directory, not a symlink alias. Strict ancestor checks also reject macOS `/tmp` or `/var` aliases. / 使用真實路徑；本版嚴格拒絕上層 symlink，包括系統別名。 |
| Missing guide pictures / 圖片缺失 | The code-review delivery has not retrieved original media. Restore pinned assets locally and perform human review before public packaging. / 補回原檔並人工審核後才可公開打包。 |

Export status uses an allowlist and omits account names, Tunnel IDs, scenes, PIDs,
raw logs and paths. Never publish your state folder or a raw diagnostic log.
The export is a snapshot, not proof of an actual web call.
狀態匯出只保留分類，不含帳戶、通道 ID、場景、PID、原始紀錄或路徑；它不是網頁呼叫證明。

Do not automatically repeat a failed modeling request. Its effect may already
have reached Blender even if the response was lost. / 建模回覆遺失不代表沒有執行，勿自動重試。
