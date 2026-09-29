# Candidate acceptance / 候選版驗收

**Historical candidate checklist:** this section records the earlier delivery, not the later 2026-09-29 web check. The original images are now present and approved for public distribution; see [verification evidence](VERIFICATION_EVIDENCE.md) for the later, narrower web observations. Full-machine acceptance remains incomplete. / **歷史候選版清單：**下文記錄較早的交付階段，並非 2026-09-29 後續網頁測試。原圖現已齊備並獲准公開發佈；較新的有限網頁實測見[驗證證據](VERIFICATION_EVIDENCE.md)。整機完整驗收仍未完成。

Automated tests in this delivery exercise real Python filesystem operations and
synthetic service/metrics responses in a Linux sandbox. They are not a test of
macOS launchd, Keychain, Tk/Aqua, OpenAI credentials or an actual ChatGPT account.
See the separate CODEX return test report for the executed count, command and log.
Historical v2.0.0/v2.0.1-rc1 results do not certify the current 2.0.1-rc2 candidate. The public export has no `tests/` directory; do not run test discovery in this checkout or treat a missing suite as a pass.
The three original test files were read but were not executed against rc2 here.
The new test_rc2 suite is not a claim that full-repository discovery passes; Codex
must reconcile legacy API/expectation changes and run the whole intended suite
before deployment. 原有三份測試只讀過，未在 rc2 執行；不可把新測試結果當成全 repository 測試通過。

| Gate / 驗收項目 | Required evidence / 所需證據 | Earlier delivery / 較早階段 |
|---|---|---|
| Candidate tests / 候選測試 | Historical private-source suite, not available in this public checkout / 私人來源的歷史測試套件；公開 repo 不包含 `tests/` | Executed in Linux at the earlier delivery; not rerun here / 較早階段於 Linux 執行；本次未重跑 |
| Real install/update/rollback / 實機安裝更新還原 | Correct configured labels, receipt/bundle version/hash; preserve settings and live Blender | Not executed / 未執行 |
| launchd lifecycle / 服務生命週期 | One tunnel PID; Stop survives login; no second supervisor; no Blender termination | Mocked behavior only / 只有模擬行為測試 |
| Network outage/recovery / 中斷恢復 | Observe naturally occurring offline/IP change/resume without changing network settings; recent failure revokes normal | Synthetic fixtures only / 只有合成測試 |
| Region rejection / 地區 403 | Actual structured error is displayed while local ready does not imply cloud ready | Synthetic fixture only / 只有合成測試 |
| Web round trip / 網頁工具 | Two real `get_scene_info` results, correct scene/object count; record approvals and failures | Not executed / 未執行 |
| Existing models / 既有模型 | Owner confirms active scenes and unsaved edits unchanged; no automatic mutation retry | No live Blender accessed / 未接觸實機 |
| Keychain and downloads / 金鑰與下載 | Existing binding unchanged; pinned artifacts verify on actual Mac | Not executed / 未執行 |
| Pictures and UI / 圖片介面 | Restore originals, human pixel/metadata review; inspect rc2 window and guide on Mac | Not executed / 未執行 |
| Architectures / 架構 | Apple silicon and Intel separately, Python 3.10 and recommended versions separately | Not executed / 未執行 |
| Power loss / 斷電 | Controlled, separately authorized durability exercise, not just process termination | Not executed / 未執行 |

Never alter VPN/Tailscale/routes/DNS/proxy as part of this acceptance. Never reset
Blender or overwrite an open project. For a model-changing request whose response
was lost, inspect the result before a separately approved retry. A simulated test
must stay labeled simulated, even when its assertions pass.

For the present source tree, inspect the existing assets and the approval record
before using `tools/build_public.py`. A hash match alone is not a human review.
現有原始碼已包含圖檔；公開打包前仍應核對圖片與批准紀錄，雜湊相符本身不等於人工覆核。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter
