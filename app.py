# app.py（起動確認用の最小構成）
from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.get("/")
def form():
    return render_template("index.html", message=None)

@app.post("/")
def handle_upload():
    f = request.files.get("file")
    msg = f"受け取りOK：{f.filename}" if f else "ファイルがありません"
    return render_template("index.html", message=msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ★RenderのPORTを使う
    app.run(host="0.0.0.0", port=port)
