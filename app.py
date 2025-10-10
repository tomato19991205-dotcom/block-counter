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

        if filename.endswith('.pdf'):
            # PDFを画像に変換
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            page = pdf.load_page(0)
            pix = page.get_pixmap()

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

        # 🔽 この1行を追加！
        img = img.copy()

try:
    
    
    
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

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < 200 or area > 50000:
            continue
        aspect = w / h
        if 1.0 < aspect < 8.0:
            block_count += 1
            total_length += w
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

except Exception as e:
    return render_template('index.html', result={'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
