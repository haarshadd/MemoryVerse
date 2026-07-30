"""
Module 1: AI Data Ingestion
Extracts raw text from whatever file type the user uploads, so downstream
steps (categorization, embedding) all work off a common plain-text schema.
"""
import os
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract


def extract_text(file_path: str) -> str:
    """Route to the right parser based on file extension. Returns raw text."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".webp"):
        return _extract_image(file_path)
    elif ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # Fall back to OCR-ish behavior isn't done here; scanned PDFs with no
    # text layer will return empty string — flag this upstream if needed.
    return text.strip()


def _extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs).strip()


def _extract_image(file_path: str) -> str:
    """OCR for scanned certificates / screenshots."""
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        # Tesseract binary may not be installed — degrade gracefully.
        return f"[OCR unavailable: {e}]"
