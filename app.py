from flask import Flask, render_template, request
from pdf2image import convert_from_bytes
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', result=None)

@app.route('/', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return render_template('index.html', result={'error': 'ファイルが選択されていません。'})

    try:    
    #----改良版ブロック検出----
    　　　　# グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ノイズ除去
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # エッジ検出
    edges = cv2.Canny(blur, 80, 180)

    # 線を太らせて連続性を上げる
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)

    # 輪郭を検出
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    block_count = 0
    total_length = 0

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # 小さすぎる線、文字、寸法などを除外
        if w > 40 and h > 10:
            aspect = w / h
            if 1.5 < aspect < 8:  # 横長すぎず縦長すぎない長方形
                block_count += 1
                total_length += w
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 結果画像をBase64に変換
    _, buffer = cv2.imencode('.png', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    result = {
        'block_count': block_count,
        'total_length': total_length,
        'height': 20,
        'image_base64': img_base64
    }

    return render_template('index.html', result=result)

# 🔻 これが無かったからSyntaxErrorが出てた！
except Exception as e:
    return render_template('index.html', result={'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
