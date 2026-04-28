"""
app/routes/main.py
晚餐輪盤系統 — 主要路由實作
"""
import random
from flask import Blueprint, redirect, render_template, request, url_for, jsonify, flash

from app.models.item import Item
from app.models.history import History

bp = Blueprint("main", __name__)

# ======================================================================
# 首頁 — 轉盤介面
# ======================================================================

@bp.route("/")
def index():
    """顯示首頁轉盤介面。"""
    items = Item.get_active()
    return render_template("index.html", items=items)

# ======================================================================
# 轉盤抽籤
# ======================================================================

@bp.route("/roll", methods=["POST"])
def roll():
    """依權重隨機抽出一個晚餐品項，寫入歷史並回傳 JSON。"""
    items = Item.get_active()
    if not items:
        return jsonify({"error": "目前沒有任何啟用的品項，請先至管理頁面新增。"}), 400

    # 根據權重隨機抽出一個品項
    weights = [i.weight for i in items]
    selected_item = random.choices(items, weights=weights, k=1)[0]

    # 寫入歷史紀錄
    try:
        History.create(item_id=selected_item.id, item_name=selected_item.name)
        return jsonify({
            "id": selected_item.id,
            "name": selected_item.name
        })
    except Exception as e:
        return jsonify({"error": f"記錄儲存失敗: {str(e)}"}), 500

# ======================================================================
# 品項管理 (Management)
# ======================================================================

@bp.route("/manage")
def manage():
    """顯示品項管理頁面。"""
    items = Item.get_all()
    return render_template("manage.html", items=items)

@bp.route("/manage/add", methods=["POST"])
def manage_add():
    """新增一筆晚餐品項。"""
    name = request.form.get("name", "").strip()
    weight_str = request.form.get("weight", "1")

    if not name:
        flash("品項名稱不可為空！", "error")
        return redirect(url_for("main.manage"))

    try:
        weight = int(weight_str)
        if weight < 1:
            raise ValueError()
    except ValueError:
        flash("權重必須是正整數（至少為 1）！", "error")
        return redirect(url_for("main.manage"))

    try:
        Item.create(name=name, weight=weight)
        flash(f"成功新增品項：{name}", "success")
    except Exception as e:
        flash(f"新增失敗: {str(e)}", "error")

    return redirect(url_for("main.manage"))

@bp.route("/manage/delete/<int:item_id>", methods=["POST"])
def manage_delete(item_id: int):
    """刪除指定晚餐品項。"""
    if Item.delete(item_id):
        flash("品項已刪除。", "success")
    else:
        flash("找不到該品項或刪除失敗。", "error")
    return redirect(url_for("main.manage"))

@bp.route("/manage/toggle/<int:item_id>", methods=["POST"])
def manage_toggle(item_id: int):
    """切換指定品項的啟用／停用狀態。"""
    if Item.toggle_active(item_id):
        # 這裡不顯示 flash，讓使用者操作更流暢，或者可以加一個簡單的提示
        pass
    else:
        flash("狀態切換失敗。", "error")
    return redirect(url_for("main.manage"))

@bp.route("/manage/weight/<int:item_id>", methods=["POST"])
def manage_weight(item_id: int):
    """更新指定品項的抽中機率權重。"""
    weight_str = request.form.get("weight")
    try:
        weight = int(weight_str)
        if weight < 1:
            raise ValueError()
    except (ValueError, TypeError):
        flash("權重更新失敗：必須是正整數。", "error")
        return redirect(url_for("main.manage"))

    item = Item.get_by_id(item_id)
    if not item:
        flash("找不到該品項。", "error")
        return redirect(url_for("main.manage"))

    try:
        Item.update(item_id=item_id, name=item.name, weight=weight)
        flash(f"「{item.name}」的權重已更新為 {weight}。", "success")
    except Exception as e:
        flash(f"更新失敗: {str(e)}", "error")

    return redirect(url_for("main.manage"))

# ======================================================================
# 歷史紀錄
# ======================================================================

@bp.route("/history")
def history():
    """顯示最近 20 筆抽籤歷史紀錄。"""
    records = History.get_recent(limit=20)
    return render_template("history.html", records=records)
