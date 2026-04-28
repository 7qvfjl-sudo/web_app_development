# 晚餐輪盤系統 — 路由設計文件 (ROUTES)

本文件依據 `docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/DB_DESIGN.md` 與 `docs/FLOWCHART.md`，規劃所有 Flask 路由與對應的 Jinja2 模板。

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|---|---|---|---|---|
| 首頁（轉盤介面） | GET | `/` | `templates/index.html` | 顯示轉盤與啟用中的品項清單 |
| 執行抽籤 | POST | `/roll` | — (JSON) | 依權重隨機抽一筆，寫入歷史，回傳 JSON |
| 品項管理頁面 | GET | `/manage` | `templates/manage.html` | 顯示所有品項（含停用）與操作表單 |
| 新增品項 | POST | `/manage/add` | — | 驗證並新增品項，重導向至 `/manage` |
| 刪除品項 | POST | `/manage/delete/<int:item_id>` | — | 刪除指定品項，重導向至 `/manage` |
| 切換啟用狀態 | POST | `/manage/toggle/<int:item_id>` | — | 切換 is_active，重導向至 `/manage` |
| 更新權重 | POST | `/manage/weight/<int:item_id>` | — | 更新指定品項的 weight，重導向至 `/manage` |
| 歷史紀錄頁面 | GET | `/history` | `templates/history.html` | 顯示最近 20 筆抽籤紀錄 |

---

## 2. 每個路由的詳細說明

### `GET /` — 首頁（轉盤介面）

- **輸入**：無
- **處理邏輯**：
  1. 呼叫 `Item.get_active()` 取得所有 `is_active=1` 的品項
  2. 將品項列表傳入模板
- **輸出**：渲染 `templates/index.html`，傳入 `items`（啟用品項列表）
- **錯誤處理**：若 `items` 為空，模板顯示「請先到管理頁面新增品項」提示

---

### `POST /roll` — 執行抽籤

- **輸入**：無（不需表單，由 JS 呼叫）
- **處理邏輯**：
  1. 呼叫 `Item.get_active()` 取得啟用品項（含 weight）
  2. 若品項為空，回傳 `{"error": "no_items"}` 並 HTTP 400
  3. 使用 `random.choices(items, weights=[i.weight for i in items])` 依權重隨機抽一筆
  4. 呼叫 `History.create(item.id, item.name)` 寫入紀錄
  5. 回傳 `{"id": item.id, "name": item.name}`
- **輸出**：JSON `{"id": int, "name": str}`
- **錯誤處理**：無可用品項時回傳 `{"error": "no_items"}` HTTP 400

---

### `GET /manage` — 品項管理頁面

- **輸入**：Query string `?msg=` 可選，用來顯示操作結果提示訊息
- **處理邏輯**：
  1. 呼叫 `Item.get_all()` 取得全部品項（含停用）
  2. 從 `request.args.get("msg")` 取得提示訊息（若有）
- **輸出**：渲染 `templates/manage.html`，傳入 `items`、`msg`
- **錯誤處理**：無特殊錯誤，清單為空時模板顯示空狀態提示

---

### `POST /manage/add` — 新增品項

- **輸入**（表單欄位）：
  - `name`（TEXT，必填）：品項名稱
  - `weight`（INTEGER，選填，預設 1）：權重
- **處理邏輯**：
  1. 從 `request.form` 取得 `name` 與 `weight`
  2. 驗證 `name` 不為空、`weight` 為正整數
  3. 呼叫 `Item.create(name, weight)`
  4. 重導向至 `/manage?msg=added`
- **輸出**：`redirect("/manage?msg=added")`
- **錯誤處理**：驗證失敗時 `redirect("/manage?msg=error_invalid")`

---

### `POST /manage/delete/<int:item_id>` — 刪除品項

- **輸入**：URL 參數 `item_id`（INTEGER）
- **處理邏輯**：
  1. 呼叫 `Item.delete(item_id)`
  2. 若回傳 `False`（品項不存在），重導向並附帶錯誤訊息
- **輸出**：`redirect("/manage?msg=deleted")`
- **錯誤處理**：找不到時 `redirect("/manage?msg=error_not_found")`

---

### `POST /manage/toggle/<int:item_id>` — 切換啟用狀態

- **輸入**：URL 參數 `item_id`（INTEGER）
- **處理邏輯**：
  1. 呼叫 `Item.toggle_active(item_id)`
- **輸出**：`redirect("/manage")`
- **錯誤處理**：找不到時 `redirect("/manage?msg=error_not_found")`

---

### `POST /manage/weight/<int:item_id>` — 更新品項權重

- **輸入**：
  - URL 參數 `item_id`（INTEGER）
  - 表單欄位 `weight`（INTEGER，必填）
- **處理邏輯**：
  1. 取得並驗證 `weight >= 1`
  2. 呼叫 `Item.update_weight(item_id, weight)`
- **輸出**：`redirect("/manage?msg=updated")`
- **錯誤處理**：驗證失敗或找不到時附帶對應錯誤訊息重導向

---

### `GET /history` — 歷史紀錄頁面

- **輸入**：無
- **處理邏輯**：
  1. 呼叫 `History.get_recent(limit=20)` 取得最近 20 筆
- **輸出**：渲染 `templates/history.html`，傳入 `records`
- **錯誤處理**：無紀錄時模板顯示「尚無抽籤紀錄」

---

## 3. Jinja2 模板清單

| 模板檔案 | 繼承自 | 說明 |
|---|---|---|
| `templates/base.html` | — | 共用版型（`<head>`、導覽列、`<footer>`） |
| `templates/index.html` | `base.html` | 首頁，包含轉盤 Canvas 與品項列表 |
| `templates/manage.html` | `base.html` | 品項管理，含新增表單、品項清單、刪除/切換/改權重操作 |
| `templates/history.html` | `base.html` | 歷史紀錄列表，顯示最近 20 筆 |

---

## 4. 路由骨架說明

骨架程式碼位於 `app/routes/main.py`，每個函式只含：
- `@bp.route(...)` 裝飾器
- 函式名稱
- Docstring（說明輸入、輸出與邏輯摘要）
- `pass` 佔位符（等待實作）
