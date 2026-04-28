"""
app/models/item.py
晚餐品項 Model — 負責 items 資料表的所有 CRUD 操作
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


class Item:
    """代表 items 資料表的一筆紀錄，並提供靜態方法操作資料表。"""

    def __init__(self, row: sqlite3.Row):
        self.id: int = row["id"]
        self.name: str = row["name"]
        self.weight: int = row["weight"]
        self.is_active: bool = bool(row["is_active"])
        self.created_at: str = row["created_at"]

    def to_dict(self) -> dict:
        """將物件轉為 dict，方便序列化為 JSON。"""
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    # ------------------------------------------------------------------
    # 查詢方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_all() -> list["Item"]:
        """取得所有品項（包含已停用），依建立時間升序排列。"""
        db = _get_db()
        rows = db.execute(
            "SELECT * FROM items ORDER BY created_at ASC"
        ).fetchall()
        return [Item(row) for row in rows]

    @staticmethod
    def get_active() -> list["Item"]:
        """取得所有啟用中的品項，用於轉盤抽籤。"""
        db = _get_db()
        rows = db.execute(
            "SELECT * FROM items WHERE is_active = 1 ORDER BY created_at ASC"
        ).fetchall()
        return [Item(row) for row in rows]

    @staticmethod
    def get_by_id(item_id: int) -> "Item | None":
        """依 id 取得單一品項，若不存在則回傳 None。"""
        db = _get_db()
        row = db.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        return Item(row) if row else None

    # ------------------------------------------------------------------
    # 寫入方法
    # ------------------------------------------------------------------

    @staticmethod
    def create(name: str, weight: int = 1) -> "Item":
        """新增一筆晚餐品項。

        Args:
            name: 品項名稱，不可為空。
            weight: 抽中機率權重，預設為 1。

        Returns:
            剛建立的 Item 物件。

        Raises:
            ValueError: 若 name 為空或 weight < 1。
        """
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
        return Item.get_by_id(cursor.lastrowid)

    @staticmethod
    def update_weight(item_id: int, weight: int) -> bool:
        """更新指定品項的權重。

        Returns:
            True 表示更新成功，False 表示找不到品項。
        """
        if weight < 1:
            raise ValueError("權重至少為 1")
        db = _get_db()
        cursor = db.execute(
            "UPDATE items SET weight = ? WHERE id = ?", (weight, item_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def toggle_active(item_id: int) -> bool:
        """切換品項的啟用/停用狀態。

        Returns:
            True 表示切換成功，False 表示找不到品項。
        """
        db = _get_db()
        cursor = db.execute(
            "UPDATE items SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (item_id,),
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete(item_id: int) -> bool:
        """刪除指定品項（相關 history 的 item_id 會被設為 NULL）。

        Returns:
            True 表示刪除成功，False 表示找不到品項。
        """
        db = _get_db()
        cursor = db.execute("DELETE FROM items WHERE id = ?", (item_id,))
        db.commit()
        return cursor.rowcount > 0
