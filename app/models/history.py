"""
app/models/history.py
抽籤歷史紀錄 Model — 負責 history 資料表的所有操作。
"""
import sqlite3
import logging
from datetime import datetime

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

class History:
    """代表 history 資料表的一筆紀錄。"""

    def __init__(self, row: sqlite3.Row):
        self.id = row["id"]
        self.item_id = row["item_id"]
        self.item_name = row["item_name"]
        self.drawn_at = row["drawn_at"]

    @staticmethod
    def create(item_id: int, item_name: str):
        """新增一筆抽籤歷史紀錄。"""
        try:
            db = _get_db()
            drawn_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = db.execute(
                "INSERT INTO history (item_id, item_name, drawn_at) VALUES (?, ?, ?)",
                (item_id, item_name, drawn_at)
            )
            db.commit()
            return History.get_by_id(cursor.lastrowid)
        except Exception as e:
            logger.error(f"建立歷史紀錄失敗: {e}")
            raise

    @staticmethod
    def get_all():
        """取得所有歷史紀錄。"""
        try:
            db = _get_db()
            rows = db.execute(
                "SELECT * FROM history ORDER BY drawn_at DESC"
            ).fetchall()
            return [History(row) for row in rows]
        except Exception as e:
            logger.error(f"取得所有歷史紀錄失敗: {e}")
            return []

    @staticmethod
    def get_recent(limit: int = 10):
        """取得最近 N 筆歷史紀錄。"""
        try:
            db = _get_db()
            rows = db.execute(
                "SELECT * FROM history ORDER BY drawn_at DESC LIMIT ?", (limit,)
            ).fetchall()
            return [History(row) for row in rows]
        except Exception as e:
            logger.error(f"取得最近歷史紀錄失敗: {e}")
            return []

    @staticmethod
    def get_by_id(history_id: int):
        """依 id 取得單一歷史紀錄。"""
        try:
            db = _get_db()
            row = db.execute(
                "SELECT * FROM history WHERE id = ?", (history_id,)
            ).fetchone()
            return History(row) if row else None
        except Exception as e:
            logger.error(f"取得歷史紀錄 (ID: {history_id}) 失敗: {e}")
            return None

    @staticmethod
    def delete(history_id: int):
        """刪除單筆歷史紀錄。"""
        try:
            db = _get_db()
            cursor = db.execute("DELETE FROM history WHERE id = ?", (history_id,))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"刪除歷史紀錄 (ID: {history_id}) 失敗: {e}")
            return False
