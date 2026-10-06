import os
import re
import docx2txt
from typing import Optional
from threading import Event
from pypdf import PdfReader

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_pdf(file_path: str, cancel_event: Optional[Event] = None) -> str:
    extracted_text = []
    reader = PdfReader(file_path)
    for page in reader.pages:
        if cancel_event and cancel_event.is_set():
            return ""
        text = page.extract_text()
        if text:
            extracted_text.append(text)
    raw_text = " ".join(extracted_text)
    return clean_text(raw_text)


def extract_text_from_docx(file_path: str) -> str:
    raw_text = docx2txt.process(file_path)
    return clean_text(raw_text)


def extract_text_from_doc(file_path: str) -> str:
    if not HAS_WIN32:
        raise NotImplementedError("Reading legacy .doc files requires pywin32 and Microsoft Word.")
    
    word_app = win32com.client.Dispatch("Word.Application")
    word_app.Visible = False
    doc = None
    try:
        abs_path = os.path.abspath(file_path)
        doc = word_app.Documents.Open(abs_path)
        raw_text = doc.Content.Text
        return clean_text(raw_text)
    finally:
        if doc:
            doc.Close(False)
        word_app.Quit()


def extract_document_text(file_path: str, cancel_event: Optional[Event] = None) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path, cancel_event)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".doc":
        return extract_text_from_doc(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")