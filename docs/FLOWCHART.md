# 晚餐輪盤系統 — 流程圖文件 (FLOWCHART)

本文件依據 `docs/PRD.md` 與 `docs/ARCHITECTURE.md`，以 Mermaid 語法產出兩種流程圖（使用者流程圖、系統序列圖），並附上功能清單對照表。

---

## 1. 使用者流程圖（User Flow）

描述使用者從進入網站到完成各項操作的完整路徑，涵蓋轉盤抽籤、品項管理與歷史紀錄瀏覽。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁 — 轉盤介面]

    B --> C{選擇操作}

    %% 轉盤抽籤路徑
    C -->|點擊「轉動！」| D{目前有啟用的品項嗎？}
    D -->|否| E[顯示提示：請先新增品項]
    E --> B
    D -->|是| F[POST /roll — 伺服器隨機抽籤]
    F --> G[前端轉盤動畫旋轉]
    G --> H[停止 — 顯示抽中的晚餐名稱]
    H --> I[寫入歷史紀錄]
    I --> B

    %% 管理品項路徑
    C -->|點擊「管理清單」| J[管理頁面 /manage]
    J --> K{選擇管理操作}

    K -->|新增品項| L[填寫品項名稱與權重]
    L --> M[POST /manage/add]
    M --> N{驗證成功？}
    N -->|否| O[顯示錯誤訊息]
    O --> L
    N -->|是| P[品項新增至資料庫]
    P --> J

    K -->|刪除品項| Q[點擊品項旁的刪除按鈕]
    Q --> R[POST /manage/delete/:id]
    R --> S[從資料庫移除]
    S --> J

    K -->|啟用 / 停用品項| T[點擊品項旁的切換開關]
    T --> U[POST /manage/toggle/:id]
    U --> V[更新品項 is_active 狀態]
    V --> J

    K -->|返回首頁| B

    %% 歷史紀錄路徑
    C -->|點擊「歷史紀錄」| W[歷史紀錄頁面 /history]
    W --> X[顯示最近 N 筆抽籤紀錄]
    X --> Y{繼續操作}
    Y -->|返回首頁| B
    Y -->|前往管理清單| J
```

---

## 2. 系統序列圖（Sequence Diagram）

描述使用者執行「轉盤抽籤」與「新增品項」時，各系統元件之間的完整互動流程。

### 2-1 轉盤抽籤流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (JS)
    participant Flask as Flask Route
    participant Model as Data Model
    participant DB as SQLite

    User->>Browser: 點擊「轉動！」按鈕
    Browser->>Flask: POST /roll
    Flask->>Model: 取得所有 is_active=True 的品項
    Model->>DB: SELECT * FROM items WHERE is_active=1
    DB-->>Model: 回傳品項清單（含權重）
    Model-->>Flask: 回傳品項列表
    Flask->>Flask: 依照權重隨機抽出一筆結果
    Flask->>Model: 寫入本次抽籤紀錄
    Model->>DB: INSERT INTO history (item_id, drawn_at)
    DB-->>Model: 寫入成功
    Model-->>Flask: 確認寫入
    Flask-->>Browser: 回傳 JSON {result: "麥當勞"}
    Browser->>Browser: 播放轉盤旋轉動畫
    Browser->>User: 動畫停止，顯示「今晚吃：麥當勞 🎉」
```

### 2-2 新增品項流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Data Model
    participant DB as SQLite

    User->>Browser: 填寫品項名稱與權重，點擊「新增」
    Browser->>Flask: POST /manage/add (name, weight)
    Flask->>Flask: 驗證輸入（名稱不為空、權重為正整數）
    alt 驗證失敗
        Flask-->>Browser: 回傳錯誤訊息
        Browser->>User: 顯示「輸入有誤，請再確認」
    else 驗證成功
        Flask->>Model: 建立新 Item 物件
        Model->>DB: INSERT INTO items (name, weight, is_active)
        DB-->>Model: 寫入成功
        Model-->>Flask: 新品項已建立
        Flask-->>Browser: 重導向至 /manage
        Browser->>User: 顯示更新後的品項清單
    end
```

### 2-3 啟用 / 停用品項流程

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Data Model
    participant DB as SQLite

    User->>Browser: 點擊品項的啟用/停用切換開關
    Browser->>Flask: POST /manage/toggle/:id
    Flask->>Model: 查詢指定 item_id
    Model->>DB: SELECT * FROM items WHERE id=:id
    DB-->>Model: 回傳該品項資料
    Model->>Model: 切換 is_active 布林值
    Model->>DB: UPDATE items SET is_active=:new_value WHERE id=:id
    DB-->>Model: 更新成功
    Model-->>Flask: 回傳結果
    Flask-->>Browser: 重導向至 /manage
    Browser->>User: 顯示更新後的狀態
```

---

## 3. 功能清單對照表

| 功能說明 | URL 路徑 | HTTP 方法 | 對應模板 / 回應 |
|---|---|---|---|
| 首頁（轉盤介面） | `/` | GET | `templates/index.html` |
| 執行轉盤抽籤 | `/roll` | POST | JSON `{result: "品項名稱"}` |
| 品項管理頁面 | `/manage` | GET | `templates/manage.html` |
| 新增晚餐品項 | `/manage/add` | POST | 重導向至 `/manage` |
| 刪除晚餐品項 | `/manage/delete/<id>` | POST | 重導向至 `/manage` |
| 啟用 / 停用品項 | `/manage/toggle/<id>` | POST | 重導向至 `/manage` |
| 查看歷史紀錄 | `/history` | GET | `templates/history.html` |

---

> **說明**：
> - 所有寫入操作（新增、刪除、切換）均採用 `POST` 方法，符合 HTTP 語意。
> - 轉盤抽籤回傳 JSON，讓前端 `roulette.js` 接收後驅動動畫，避免頁面整個重新載入。
> - 品項的 `weight`（權重）欄位決定在轉盤上的面積比例與被抽中的機率。
> - `is_active` 欄位讓使用者可以暫時停用品項，而不需要刪除資料。
