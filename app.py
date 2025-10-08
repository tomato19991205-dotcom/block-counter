import os
import tempfile
import fitz  # PyMuPDF
import cv2
import numpy as np
from flask import Flask, render_template, request
from waitress import serve
from PIL import Image
import base64

app = Flask(__name__)

def detect_blocks(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    block_count = 0
    total_length = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # 四角形っぽい大きさのものだけカウント
        if 30 < w < 400 and 15 < h < 300:
            block_count += 1
            total_length += w
            # 赤枠を描画
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 結果画像をBase64に変換
    _, buffer = cv2.imencode('.png', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    return block_count, total_length, img_b64

@app.route('/')
def index():
    return render_template('index.html', result=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return render_template('index.html', result={'error': 'ファイルがありません'})

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    file.save(temp_pdf.name)

    pdf = fitz.open(temp_pdf.name)
    first_page = pdf.load_page(0)
    pix = first_page.get_pixmap(dpi=200)
    img_path = temp_pdf.name.replace(".pdf", ".png")
    pix.save(img_path)

    block_count, total_length, img_b64 = detect_blocks(img_path)

    os.remove(temp_pdf.name)
    os.remove(img_path)

    return render_template(
        'index.html',
        result={
            'blocks': block_count,
            'total_length': total_length,
            'height': 20,
            'image': img_b64
        }
    )

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=10000)
