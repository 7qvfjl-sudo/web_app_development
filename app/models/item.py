"""
app/models/item.py
晚餐品項 Model — 負責 items 資料表的所有 CRUD 操作。
"""
import sqlite3
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_db():
    """取得目前 Flask app context 中的資料庫連線。"""
    from flask import g, current_app
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

class Item:
    """代表 items 資料表的一筆紀錄。"""

    def __init__(self, row: sqlite3.Row):
        self.id = row["id"]
        self.name = row["name"]
        self.weight = row["weight"]
        self.is_active = bool(row["is_active"])
        self.created_at = row["created_at"]

    @staticmethod
    def create(name: str, weight: int = 1):
        """新增一筆晚餐品項。"""
        try:
            name = name.strip()
            if not name:
                raise ValueError("品項名稱不可為空")
            if weight < 1:
                raise ValueError("權重至少為 1")

            db = _get_db()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = db.execute(
                "INSERT INTO items (name, weight, is_active, created_at) VALUES (?, ?, 1, ?)",
                (name, weight, created_at),
            )
            db.commit()
            logger.info(f"成功新增品項: {name} (ID: {cursor.lastrowid})")
            return Item.get_by_id(cursor.lastrowid)
        except Exception as e:
            logger.error(f"新增品項失敗: {e}")
            raise

    @staticmethod
    def get_all():
        """取得所有品項。"""
        try:
            db = _get_db()
            rows = db.execute(
                "SELECT * FROM items ORDER BY created_at ASC"
            ).fetchall()
            return [Item(row) for row in rows]
        except Exception as e:
            logger.error(f"取得所有品項失敗: {e}")
            return []

    @staticmethod
    def get_active():
        """取得所有啟用中的品項。"""
        try:
            db = _get_db()
            rows = db.execute(
                "SELECT * FROM items WHERE is_active = 1"
            ).fetchall()
            return [Item(row) for row in rows]
        except Exception as e:
            logger.error(f"取得啟用品項失敗: {e}")
            return []

    @staticmethod
    def get_by_id(item_id: int):
        """依 id 取得單一品項。"""
        try:
            db = _get_db()
            row = db.execute(
                "SELECT * FROM items WHERE id = ?", (item_id,)
            ).fetchone()
            return Item(row) if row else None
        except Exception as e:
            logger.error(f"取得品項 (ID: {item_id}) 失敗: {e}")
            return None

    @staticmethod
    def update(item_id: int, name: str, weight: int):
        """更新品項名稱與權重。"""
        try:
            if not name.strip():
                raise ValueError("品項名稱不可為空")
            if weight < 1:
                raise ValueError("權重至少為 1")

            db = _get_db()
            cursor = db.execute(
                "UPDATE items SET name = ?, weight = ? WHERE id = ?",
                (name.strip(), weight, item_id)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新品項 (ID: {item_id}) 失敗: {e}")
            raise

    @staticmethod
    def toggle_active(item_id: int):
        """切換啟用/停用狀態。"""
        try:
            db = _get_db()
            cursor = db.execute(
                "UPDATE items SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
                (item_id,)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"切換品項 (ID: {item_id}) 狀態失敗: {e}")
            return False

    @staticmethod
    def delete(item_id: int):
        """刪除品項。"""
        try:
            db = _get_db()
            cursor = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
            db.commit()
            logger.info(f"成功刪除品項 ID: {item_id}")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"刪除品項 (ID: {item_id}) 失敗: {e}")
            return False
