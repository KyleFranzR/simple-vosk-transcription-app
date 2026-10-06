import os
import re
from typing import Optional
from threading import Event
from PIL import Image
import pytesseract

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESSERACT_PATH = os.path.join(BASE_DIR, "Tesseract-OCR", "tesseract.exe")

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_image(file_path: str, cancel_event: Optional[Event] = None) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    supported_extensions = [".bmp", ".jpeg", ".jpg", ".png"]

    if ext not in supported_extensions:
        raise ValueError(f"Unsupported image format: {ext}")

    if cancel_event and cancel_event.is_set():
        return ""

    try:
        image = Image.open(file_path)
        raw_text = pytesseract.image_to_string(image)
        return clean_text(raw_text)
    except Exception as e:
        raise RuntimeError(f"OCR processing failed for {file_path}: {e}")