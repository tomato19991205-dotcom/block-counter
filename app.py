# app.py
from flask import Flask, render_template, request
import cv2
import numpy as np
import fitz  # PyMuPDF
import base64

app = Flask(__name__)

def pdf_to_image(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    return img

def detect_blocks(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
