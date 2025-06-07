import pytesseract
from PIL import Image
import pdfplumber
import os

def extract_text_from_file(path):
    text = ""
    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif path.endswith((".png", ".jpg", ".jpeg")):
        text = pytesseract.image_to_string(Image.open(path))
    else:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    return text
