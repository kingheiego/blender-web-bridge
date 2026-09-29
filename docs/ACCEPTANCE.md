# Candidate acceptance / 候選版驗收

**Status: NOT hardware-accepted; public release blocked pending original media review.**
**狀態：未完成實機驗收；原圖取回及人工覆核前阻擋公開發佈。**

Automated tests in this delivery exercise real Python filesystem operations and
synthetic service/metrics responses in a Linux sandbox. They are not a test of
macOS launchd, Keychain, Tk/Aqua, OpenAI credentials or an actual ChatGPT account.
See the separate CODEX return test report for the executed count, command and log.
Historical v2.0.0/v2.0.1-rc1 results do not certify this candidate.
The three original test files were read but were not executed against rc2 here.
The new test_rc2 suite is not a claim that full-repository discovery passes; Codex
must reconcile legacy API/expectation changes and run the whole intended suite
before deployment. 原有三份測試只讀過，未在 rc2 執行；不可把新測試結果當成全 repository 測試通過。

| Gate / 驗收項目 | Required evidence / 所需證據 | This delivery / 本次 |
|---|---|---|
| Candidate tests / 候選測試 | Run `python3 -m unittest discover -s tests -p 'test_rc2_*.py' -v` | Executed in Linux; see report / Linux 已執行 |
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

To finish media assembly from an already available pinned local checkout:
`python3 tools/complete_source.py --baseline-repo <local-checkout>`.
This does not fetch, push, deploy, run Blender or touch account settings.
Then inspect every asset and update `release-assets.json` truthfully before using
`tools/build_public.py`. Do not mark a review as complete merely because hashes match.
