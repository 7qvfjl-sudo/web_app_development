-- 晚餐輪盤系統 — SQLite Schema
-- 建立順序：items 先建（history 有外鍵依賴 items）

PRAGMA foreign_keys = ON;

-- -------------------------------------------------------
-- 資料表：items（晚餐品項）
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    weight     INTEGER NOT NULL DEFAULT 1 CHECK (weight >= 1),
    is_active  INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- -------------------------------------------------------
-- 資料表：history（抽籤歷史紀錄）
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id   INTEGER REFERENCES items(id) ON DELETE SET NULL,
    item_name TEXT    NOT NULL,
    drawn_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
