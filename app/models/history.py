"""
app/models/history.py
抽籤歷史紀錄 Model — 負責 history 資料表的所有操作
"""
import sqlite3
from datetime import datetime


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
    """代表 history 資料表的一筆紀錄，並提供靜態方法操作資料表。"""

    def __init__(self, row: sqlite3.Row):
        self.id: int = row["id"]
        self.item_id: int | None = row["item_id"]
        self.item_name: str = row["item_name"]
        self.drawn_at: str = row["drawn_at"]

    def to_dict(self) -> dict:
        """將物件轉為 dict，方便序列化為 JSON。"""
        return {
            "id": self.id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "drawn_at": self.drawn_at,
        }

    # ------------------------------------------------------------------
    # 查詢方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_all() -> list["History"]:
        """取得所有歷史紀錄，依抽籤時間降序排列（最新的在前）。"""
        db = _get_db()
        rows = db.execute(
            "SELECT * FROM history ORDER BY drawn_at DESC"
        ).fetchall()
        return [History(row) for row in rows]

    @staticmethod
    def get_recent(limit: int = 10) -> list["History"]:
        """取得最近 N 筆歷史紀錄。

        Args:
            limit: 回傳筆數上限，預設 10 筆。

        Returns:
            最近 N 筆抽籤紀錄的 History 物件列表。
        """
        db = _get_db()
        rows = db.execute(
            "SELECT * FROM history ORDER BY drawn_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [History(row) for row in rows]

    # ------------------------------------------------------------------
    # 寫入方法
    # ------------------------------------------------------------------

    @staticmethod
    def create(item_id: int, item_name: str) -> "History":
        """新增一筆抽籤歷史紀錄。

        Args:
            item_id: 被抽中品項的 id。
            item_name: 被抽中品項的名稱快照（防止品項刪除後資料遺失）。

        Returns:
            剛建立的 History 物件。
        """
        item_name = item_name.strip()
        if not item_name:
            raise ValueError("品項名稱不可為空")

        db = _get_db()
        drawn_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.execute(
            "INSERT INTO history (item_id, item_name, drawn_at) VALUES (?, ?, ?)",
            (item_id, item_name, drawn_at),
        )
        db.commit()

        row = db.execute(
            "SELECT * FROM history WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return History(row)
