import tempfile
import pdfplumber
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    # Renderでは一時フォルダを使う
    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    file.save(temp_path)

    # PDFを解析
    with pdfplumber.open(temp_path) as pdf:
        total_length = 0
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                total_length += len(text)

    return jsonify({"result": f"解析完了: {total_length}文字分のデータを検出しました！"})

if __name__ == '__main__':
    # RenderではWaitressを使う（Flask標準サーバーだと警告が出る）
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)
