import os, tempfile
import pdfplumber
from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files or request.files["file"].filename == "":
        return render_template("index.html", result={"error": "PDFが選択されていません"})

    f = request.files["file"]
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        f.save(tmp.name)
        temp_path = tmp.name

    try:
        # ここは仮ロジック（まずは動くことを優先）
        total_length = 0
        count = 0
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                total_length += len(text)
                count += text.count("CB")  # 仮の数え方

        return render_template("index.html", result={
            "count": count,
            "total_length": total_length,
            "height": "20cm（仮）"
        })
    except Exception as e:
        return render_template("index.html", result={"error": str(e)})
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    serve(app, host="0.0.0.0", port=port)  # Render向け
