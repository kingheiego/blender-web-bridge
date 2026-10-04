# 路徑安全回歸測試

公開附 15 項可獨立重跑的安全回歸，使用合成檔案、模擬下載和暫存目錄；不讀真實秘密、不連 Blender、不啟動通道。完整來源的 202 項測試另包括安裝器、生命週期及健康狀態測試；不能把本資料夾說成全部 202 項。

在 repository 根目錄，用 Python 3.10 或以上執行：

```sh
BWB_TEST_ROOT="$(python3 -c 'import pathlib,tempfile; print(pathlib.Path(tempfile.mkdtemp(prefix="bwb-tests-")).resolve())')"
TMPDIR="$BWB_TEST_ROOT" BLENDER_WEB_BRIDGE_DATA="$BWB_TEST_ROOT/state" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_rc3_path_safety.py' -v
```

暫存根目錄使用實體路徑，避免 macOS 的 `/tmp` 或 `/var` 系統符號連結被刻意嚴格的路徑檢查拒絕。測試不更改 Keychain 或既有帳戶設定。

---
Watermark / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
