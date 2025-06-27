# pdf_reader.py
import pdfplumber
import os

def extract_text_from_pdf(file_path):
    """
    Extracts all text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from all pages.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    
    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")
    
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n\n--- Page {i+1} ---\n" + page_text.strip()
    
    if not text.strip():
        raise ValueError("PDF has no extractable text.")

    return text.strip()
