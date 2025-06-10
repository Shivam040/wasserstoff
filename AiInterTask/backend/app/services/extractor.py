import pytesseract
from PIL import Image
import pdfplumber
import os

def extract_text_with_metadata(file_path: str):
    """
    Extracts text from PDF/image/txt and returns a list of
    dictionaries with page number, paragraph number, and text.
    """
    extracted_data = []

    if file_path.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
                        for para_num, para in enumerate(paragraphs, start=1):
                            extracted_data.append({
                                "page": page_num,
                                "para": para_num,
                                "text": para
                            })
        except Exception as e:
            print(f"[ERROR] PDF extract failed: {e}")

    elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
        try:
            image = Image.open(file_path)
            ocr_text = pytesseract.image_to_string(image)
            paragraphs = [p.strip() for p in ocr_text.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs, start=1):
                extracted_data.append({
                    "page": 1,
                    "para": i,
                    "text": para
                })
        except Exception as e:
            print(f"[ERROR] OCR extract failed: {e}")

    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                txt_text = f.read()
            paragraphs = [p.strip() for p in txt_text.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs, start=1):
                extracted_data.append({
                    "page": 1,
                    "para": i,
                    "text": para
                })
        except Exception as e:
            print(f"[ERROR] TXT read failed: {e}")

    else:
        print(f"[WARNING] Unsupported file type: {file_path}")

    return extracted_data
