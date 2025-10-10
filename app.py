from flask import Flask, render_template, request
import cv2
import numpy as np
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

        # ===== PDFを画像に変換 =====
        if filename.endswith('.pdf'):
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            page = pdf.load_page(0)
            pix = page.get_pixmap()
            img_data = np.frombuffer(pix.samples, dtype=np.uint8)
            if pix.alpha:  # RGBA画像の場合
                img = img_data.reshape(pix.height, pix.width, 4)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            else:
                img = img_data.reshape(pix.height, pix.width, 3)
        else:
            # 通常の画像を読み込み
            img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        # ===== 画像処理 =====
        if img is None or img.size == 0:
            raise ValueError("画像の読み込みに失敗しました。")

        # 🔧 OpenCVの描画エラー対策
        img = img.copy()

        # ここから検出処理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            25, 10
        )
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        block_count = 0
        total_length = 0

try:
     for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h

        # 小さいノイズや大きすぎる枠を除外
        if area < 1000 or area > 80000:
            continue

        aspect = w / h

        # ブロックの形（横長）をより限定
        if 3.0 < aspect < 7.0 and 20 < h < 200:
            block_count += 1
            total_length += w
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

except Exception as e:
    return render_template('index.html', result={'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
