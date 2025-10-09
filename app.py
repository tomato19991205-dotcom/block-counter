from flask import Flask, render_template, request
from pdf2image import convert_from_bytes
import cv2
import numpy as np
import io
import base64
import fitz  # PyMuPDF


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('index.html')

    file = request.files['file']
    if not file:
        return render_template('index.html', result={'error': 'ファイルが選択されていません'})

    try:
        filename = file.filename.lower()

    if filename.endswith('.pdf'):
        # PDFを画像に変換
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        page = pdf.load_page(0)
        pix = page.get_pixmap()

        # 画像データのチャンネル数に応じて処理を分ける
        img_data = np.frombuffer(pix.samples, dtype=np.uint8)

        if pix.alpha:  # RGBA画像
            img = img_data.reshape(pix.height, pix.width, 4)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
     else:
     try:
                img = img_data.reshape(pix.height, pix.width, 3)
            except:
                img = img_data.reshape(pix.height, pix.width)
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
     else:
        # 通常の画像を読み込み
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    # ===== ここから画像処理 =====
    if img is None or img.size == 0:
        raise ValueError("画像の読み込みに失敗しました。")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 80, 180)
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    block_count = 0
    total_length = 0

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 40 and h > 10:
            aspect = w / h
            if 1.5 < aspect < 8:
                block_count += 1
                total_length += w
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    _, buffer = cv2.imencode('.png', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    result = {
        'block_count': block_count,
        'total_length': total_length,
        'height': 20,
        'image_base64': img_base64
    }

    return render_template('index.html', result=result)

except Exception as e:
    return render_template('index.html', result={'error': str(e)})
    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
