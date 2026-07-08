"""
parser.py
---------
Extracts raw text from uploaded resume / job description files.
Supports PDF, DOCX and plain text.
"""

import io
import pdfplumber
import docx


def extract_text(uploaded_file) -> str:
    """
    Extract text from a file-like object (Streamlit UploadedFile or a path).
    Supports .pdf, .docx and .txt
    """
    name = getattr(uploaded_file, "name", str(uploaded_file)).lower()

    if name.endswith(".pdf"):
        return _extract_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return _extract_docx(uploaded_file)
    elif name.endswith(".txt"):
        return _extract_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {name}. Please upload PDF, DOCX or TXT.")


def _extract_pdf(file_obj) -> str:
    text_chunks = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def _extract_docx(file_obj) -> str:
    document = docx.Document(file_obj)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def _extract_txt(file_obj) -> str:
    if hasattr(file_obj, "read"):
        raw = file_obj.read()
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="ignore")
        return raw
    with open(file_obj, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean_text(text: str) -> str:
    """Light normalization: collapse whitespace, strip control chars."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)
