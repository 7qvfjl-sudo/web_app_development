"""
app.py — Flask 應用程式主要進入點
執行方式：
    python app.py          # 直接啟動（開發模式）
    flask --app app run    # 或用 flask CLI

初始化資料庫（第一次執行前）：
    flask --app app init-db
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
