"""
app/routes/main.py
晚餐輪盤系統 — 主要路由骨架
所有路由均掛載於此 Blueprint，實作邏輯於階段六完成。
"""
import random

from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.models.item import Item
from app.models.history import History

bp = Blueprint("main", __name__)


# ======================================================================
# 首頁 — 轉盤介面
# ======================================================================

@bp.route("/")
def index():
    """顯示首頁轉盤介面。

    輸入：無
    處理：取得所有啟用中的品項（Item.get_active()），傳入模板
    輸出：渲染 templates/index.html，傳入 items（啟用品項列表）
    錯誤：items 為空時模板顯示提示訊息
    """
    pass


# ======================================================================
# 轉盤抽籤
# ======================================================================

@bp.route("/roll", methods=["POST"])
def roll():
    """依權重隨機抽出一個晚餐品項，寫入歷史並回傳 JSON。

    輸入：無（由前端 JS 以 fetch POST 呼叫）
    處理：
        1. Item.get_active() 取得啟用品項
        2. random.choices() 依 weight 加權抽籤
        3. History.create() 寫入紀錄
    輸出：JSON {"id": int, "name": str}
    錯誤：無啟用品項時回傳 {"error": "no_items"} HTTP 400
    """
    pass


# ======================================================================
# 品項管理
# ======================================================================

@bp.route("/manage")
def manage():
    """顯示品項管理頁面。

    輸入：Query string ?msg= 可選（操作結果提示）
    處理：Item.get_all() 取得所有品項（含停用）
    輸出：渲染 templates/manage.html，傳入 items、msg
    """
    pass


@bp.route("/manage/add", methods=["POST"])
def manage_add():
    """新增一筆晚餐品項。

    輸入（表單）：name（TEXT 必填）、weight（INTEGER 選填，預設 1）
    處理：驗證輸入 → Item.create(name, weight)
    輸出：redirect("/manage?msg=added")
    錯誤：驗證失敗 → redirect("/manage?msg=error_invalid")
    """
    pass


@bp.route("/manage/delete/<int:item_id>", methods=["POST"])
def manage_delete(item_id: int):
    """刪除指定晚餐品項。

    輸入：URL 參數 item_id（INTEGER）
    處理：Item.delete(item_id)
    輸出：redirect("/manage?msg=deleted")
    錯誤：找不到品項 → redirect("/manage?msg=error_not_found")
    """
    pass


@bp.route("/manage/toggle/<int:item_id>", methods=["POST"])
def manage_toggle(item_id: int):
    """切換指定品項的啟用／停用狀態。

    輸入：URL 參數 item_id（INTEGER）
    處理：Item.toggle_active(item_id)
    輸出：redirect("/manage")
    錯誤：找不到品項 → redirect("/manage?msg=error_not_found")
    """
    pass


@bp.route("/manage/weight/<int:item_id>", methods=["POST"])
def manage_weight(item_id: int):
    """更新指定品項的抽中機率權重。

    輸入：URL 參數 item_id（INTEGER）；表單 weight（INTEGER 必填，≥1）
    處理：驗證 → Item.update_weight(item_id, weight)
    輸出：redirect("/manage?msg=updated")
    錯誤：驗證失敗 → redirect("/manage?msg=error_invalid")
          找不到品項 → redirect("/manage?msg=error_not_found")
    """
    pass


# ======================================================================
# 歷史紀錄
# ======================================================================

@bp.route("/history")
def history():
    """顯示最近 20 筆抽籤歷史紀錄。

    輸入：無
    處理：History.get_recent(limit=20)
    輸出：渲染 templates/history.html，傳入 records
    錯誤：無紀錄時模板顯示空狀態提示
    """
    pass
