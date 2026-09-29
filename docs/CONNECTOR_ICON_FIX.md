# Connector icon: asset ready, ChatGPT-side setting pending / 連接器圖示：檔案已備妥，仍待 ChatGPT 端設定

## English

The public icon is [assets/icon.png](../assets/icon.png), a real **1024 × 1024 PNG** converted from the desktop app's existing icon. It shows a white outline cube on a dark rounded square. Its SHA-256 is `260251f0c7bde66d407a2f62706772eb97dd91e3b5c3829b5d882094a1268a56`. The matching macOS icon is [assets/icon.icns](../assets/icon.icns).

Use this **direct image URL** for a branding field that accepts an icon/logo URL:

`https://raw.githubusercontent.com/kingheiego/blender-web-bridge/main/assets/icon.png`

The repository cannot set the icon shown beside an app name in ChatGPT. On **2026-09-29**, the app's ChatGPT detail page rendered OpenAI's built-in inline SVG placeholder (`img src` begins `data:image/svg+xml,`), **not a remote image URL**. There was therefore no remote icon URL on that page to test for a 404. The visible result is consistent with an unset app icon, but the underlying metadata value was not exposed.

Read-only inspection found **no icon/logo URL field** in **ChatGPT → Plugins → your app → More actions → Manage**. That page offered **Manage app → App name** and **App description** edits, plus **Refresh tools**. **OpenAI Platform → organization settings → Tunnels** also had no icon field, and the inspected project **Plugins** page did not list this ChatGPT app. We cannot truthfully name an editable icon field or its current stored value from those pages.

To finish the ChatGPT-side fix:

1. Open the direct PNG URL above after the `main` update is published and confirm it shows the cube image.
2. In ChatGPT, open **Plugins → your app → More actions → Manage** and look for an owner/developer branding or app-icon editor. The inspected Manage page did **not** expose one. Do **not** put the image URL in **App name**, **App description**, **Tunnel ID**, or the runtime-key field.
3. If your OpenAI developer/app branding interface exposes an **app icon/logo image URL** field, enter the direct PNG URL there and save; reload the ChatGPT app detail and confirm it shows the cube. If no such field appears, ask OpenAI support how this dev-mode app's icon metadata can be set. A repo commit alone cannot change the ChatGPT placeholder.

The owner must make that account-side setting, or explicitly authorize a browser edit once the correct field is available. No ChatGPT-side setting was changed in this documentation update.

## 繁體中文

公開圖示是 [assets/icon.png](../assets/icon.png)：由既有桌面 App 圖示轉出的真正 **1024 × 1024 PNG**，畫面為深色圓角方塊上的白色線框立方體。其 SHA-256 為 `260251f0c7bde66d407a2f62706772eb97dd91e3b5c3829b5d882094a1268a56`。對應的 macOS 圖示為 [assets/icon.icns](../assets/icon.icns)。

若品牌設定有接受圖示／標誌網址的欄位，應填上面同一條 **PNG 原始檔直連網址**。

此 repo 不能直接設定 ChatGPT 中 App 名稱旁的圖示。**2026-09-29** 實際檢查時，ChatGPT App 詳情頁顯示 OpenAI 內建的 SVG 預設圖示（`img src` 以 `data:image/svg+xml,` 開始），**不是遠端圖片網址**，因此沒有可驗證為 404 的舊圖示網址。畫面與「尚未設定 App 圖示」相符，但頁面沒有顯示底層儲存的 metadata 值。

唯讀檢查發現 **ChatGPT → Plugins → 你的 App → More actions → Manage** 沒有圖示／標誌網址欄位；只有 **Manage app → App name**、**App description** 的編輯及 **Refresh tools**。**OpenAI Platform → organization settings → Tunnels** 也沒有圖示欄位；檢查的 project **Plugins** 頁亦沒有列出這個 ChatGPT App。因此，目前不能如實指出可編輯的圖示欄位或其儲存值。

完成 ChatGPT 端修復的方法：

1. `main` 更新公開後，打開上面的 PNG 原始檔直連網址，確認看到白色線框立方體。
2. 在 ChatGPT 打開 **Plugins → 你的 App → More actions → Manage**，查看擁有人／開發者品牌設定是否提供圖示編輯。已檢查的 Manage 頁**沒有**這欄。**不要**把圖片網址填進 **App name**、**App description**、**Tunnel ID** 或 runtime key 欄位。
3. 如果你的 OpenAI 開發者／App 品牌設定提供 **app icon／logo image URL** 欄位，在該處填入 PNG 直連網址並儲存，再重新打開 ChatGPT App 詳情，確認出現立方體。如果始終沒有此欄，請向 OpenAI 支援查詢如何設定這個 dev-mode App 的圖示 metadata。單靠 repo 提交不能改掉 ChatGPT 預設圖示。

這項帳戶端設定須由擁有人操作，或在找到正確欄位後明確授權代為在瀏覽器修改。本次文件更新**沒有**改動 ChatGPT 設定。
