import pytesseract
from PIL import Image
import pdfplumber
import os

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from PDF, image, or text file.
    """
    text = ""

    if file_path.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"[ERROR] PDF extract failed: {e}")

    elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"[ERROR] OCR extract failed: {e}")

    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"[ERROR] TXT read failed: {e}")

    else:
        print(f"[WARNING] Unsupported file type: {file_path}")

    return text.strip()
