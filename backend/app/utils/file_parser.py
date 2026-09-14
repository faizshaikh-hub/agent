"""
Utility for extracting text from uploaded files (PDF, plain text, email).
"""
import io
from typing import Optional


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text content from an uploaded file.

    Args:
        file_content: Raw file bytes.
        filename: Original filename (used to determine type).

    Returns:
        Extracted text string.
    """
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return _extract_from_pdf(file_content)
    elif lower_name.endswith((".txt", ".eml", ".msg", ".text")):
        return _extract_from_text(file_content)
    elif lower_name.endswith((".html", ".htm")):
        return _extract_from_html(file_content)
    else:
        # Try as plain text
        return _extract_from_text(file_content)


def _extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"


def _extract_from_text(content: bytes) -> str:
    """Extract text from plain text files."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content.decode("latin-1")
        except Exception:
            return content.decode("utf-8", errors="replace")


def _extract_from_html(content: bytes) -> str:
    """Extract text from HTML, stripping tags."""
    import re
    text = _extract_from_text(content)
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean
