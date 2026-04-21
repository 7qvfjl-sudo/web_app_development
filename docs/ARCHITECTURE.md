# 晚餐輪盤系統 - 系統架構設計 (ARCHITECTURE)

## 1. 技術架構說明

本專案採用輕量級的 Web 開發技術組合，適合快速開發單純、個人用的應用系統。

- **選用技術與原因**：
  - **後端 (Python + Flask)**：Flask 是一個輕量級的 Python Web 框架，學習曲線平緩，沒有過多的預設限制，非常適合用來建立小巧實用的工具（如本系統）。
  - **前端渲染 (Jinja2)**：Jinja2 是 Flask 內建的模板引擎，可直接在 HTML 檔案中動態帶入後端的變數，並進行條件和迴圈渲染。因為本系統不採用前後端分離，因此 Jinja2 是呈現畫面的最佳解。
  - **資料庫 (SQLite)**：由於系統主要供個人使用，不需面對高併發存取，SQLite 這種無伺服器的本機資料庫是最好的選擇，資料以單一檔案（`.db`）存在，備份與遷移都很方便。

- **Flask MVC 模式說明**：
  - **Model (模型)**：負責定義資料結構（如：晚餐品項、歷史紀錄）以及對 SQLite 的寫入與讀取。
  - **View (視圖)**：負責將資料轉化為使用者能看見的介面，這裡指的是 `templates` 裡的 HTML 檔案與靜態資源（CSS、JavaScript，包括轉盤的動畫）。
  - **Controller (控制器)**：由 Flask 的 `routes` 負責，接受使用者的請求（例如：點擊抽籤、新增餐廳），向 Model 獲取或更新資料後，將結果交由 View 去重新渲染並回傳給瀏覽器。

---

## 2. 專案資料夾結構

為了讓專案更好維護，我們將程式碼根據各自的責任進行拆分，資料夾結構如下：

```text
web_app_development/
├── app/
│   ├── models/            ← 資料庫模型 (與 SQLite 溝通的邏輯)
│   │   ├── item.py        ← 負責晚餐品項 (新增、刪除、查詢)
│   │   └── history.py     ← 負責儲存過去的抽籤紀錄
│   ├── routes/            ← 路由控制器 (Flask 路由)
│   │   └── main.py        ← 定義網址路徑 (如 /、/add_item、/roll)
│   ├── templates/         ← HTML 頁面視圖 (Jinja2 渲染)
│   │   ├── base.html      ← 網站共用版型 (標題、導覽列等)
│   │   ├── index.html     ← 首頁與轉盤顯示區域
│   │   └── manage.html    ← 晚餐清單的管理頁面 (新增/修改/刪除)
│   └── static/            ← 靜態資源檔案
│       ├── css/style.css  ← 視覺樣式與轉盤設計
│       └── js/roulette.js ← 轉盤動畫效果與抽籤邏輯 (Vanilla JS)
├── instance/
│   └── database.db        ← 系統的 SQLite 資料庫檔案 (自動生成)
├── docs/                  ← 存放專案的設計文件 (PRD、架構文件等)
├── requirements.txt       ← 專案所需安裝的 Python 套件總表
└── app.py                 ← Flask 應用程式的主要進入點 (啟動伺服器)
```

---

## 3. 元件關係圖

以下展示了當使用者開啟網頁並操作時，系統各元件之間的互動流程：

```mermaid
graph TD
    User([瀏覽器 / 使用者])
    
    subgraph Flask App (伺服器端)
        Controller[Flask Route<br>(Controller)]
        View[Jinja2 Template<br>(View)]
        Model[Data Model<br>(Model)]
    end
    
    DB[(SQLite 資料庫)]
    
    User -- "1. 發送請求 (如: /roll)" --> Controller
    Controller -- "2. 查詢/寫入資料" --> Model
    Model -- "3. 實際對資料表做操作" --> DB
    DB -. "4. 回傳資料查詢結果" .-> Model
    Model -. "5. 將資料回傳給路由" .-> Controller
    Controller -- "6. 將資料塞進樣板渲染" --> View
    View -- "7. 回傳包含數據的 HTML 頁面" --> User
```

---

## 4. 關鍵設計決策

在設計本系統時，我們做了以下幾個重要的決策：

1. **傳統全端一體化 (Monolith) 設計**
   * **決策原因**：不盲目追求目前流行的「前後端分離 (React/Vue + API)」，而是選擇結合 Flask 與 Jinja2 渲染 HTML。這樣能大幅減少專案初期的複雜度與開發成本，非常適合個人小工具或 MVP（最小可行性產品）。

2. **轉盤動畫使用純前端 (Vanilla JS + CSS) 處理**
   * **決策原因**：轉盤旋轉的流暢度與視覺呈現屬於使用者的操作體驗。因此，伺服器端只負責提供「隨機抽到的結果」與「選項清單」，而實際的「轉動畫面、停止的計算」則全部透過 `static/js/roulette.js` 在瀏覽器中運算，這樣能確保動畫順暢不卡頓。

3. **統一使用 `app.py` 作為應用入口**
   * **決策原因**：將應用的啟動邏輯、擴充套件初始化、以及依賴載入整合在根目錄的單一入口。除了符合初學者友善的思考模式外，也方便在開發階段就一次看清楚系統如何將 `models`、`routes` 與 `templates` 給啟動並組合起來。
