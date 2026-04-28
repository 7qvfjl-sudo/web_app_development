"""
app/__init__.py
Flask 應用程式工廠函式（Application Factory）
負責初始化 Flask app、設定資料庫路徑、關閉連線與註冊 Blueprint
"""
import os
import sqlite3

from flask import Flask, g


def create_app(config=None) -> Flask:
    """建立並設定 Flask 應用程式。

    Args:
        config: 可選的設定 dict，用於測試時覆蓋預設值。

    Returns:
        設定完成的 Flask app 實例。
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- 預設設定 ---
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.path.join(app.instance_path, "database.db"),
    )

    if config:
        app.config.from_mapping(config)

    # 確保 instance 資料夾存在
    os.makedirs(app.instance_path, exist_ok=True)

    # --- 資料庫初始化指令 ---
    @app.cli.command("init-db")
    def init_db_command():
        """執行 `flask init-db` 初始化資料庫（建立資料表）。"""
        _init_db(app)
        print("✅ 資料庫初始化完成。")

    # --- 自動關閉資料庫連線 ---
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # --- 註冊 Blueprint ---
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


def _init_db(app: Flask):
    """讀取 schema.sql 並初始化資料庫。"""
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql"
    )
    with sqlite3.connect(app.config["DATABASE"]) as db:
        with open(schema_path, "r", encoding="utf-8") as f:
            db.executescript(f.read())
