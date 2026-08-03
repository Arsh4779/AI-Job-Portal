from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # Supports existing environments that still use PyPDF2.
    from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Return readable text from a PDF resume or raise a helpful error."""
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        raise ValueError("Password-protected PDFs are not supported.")

    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError(
            "No selectable text was found in this PDF. Upload a text-based PDF."
        )
    return text
