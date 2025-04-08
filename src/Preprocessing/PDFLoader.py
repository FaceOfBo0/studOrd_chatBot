from docling.document_converter import DocumentConverter
import pdfplumber, fitz

def ExtractTxtFromPyMuPDF(pdf_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz).
    
    Args:
        pdf_path: Path to the PDF file to extract text from.
        
    Returns:
        Extracted text as a single string.
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_textpage().extractText()
    return text

def ExtractTxtFromDocling(pdf_path) -> str:
    """Extract text from a PDF file using Docling.
    
    Args:
        pdf_path: Path to the PDF file to extract text from.
        
    Returns:
        Extracted text as a single string.
    """
    dc = DocumentConverter()
    doc = dc.convert(pdf_path).document
    return doc.export_to_text()

def ExtractTxtFromPDFPlumber(pdf_path):
    """Extract text from a PDF file using PDFPlumber.
    
    Args:
        pdf_path: Path to the PDF file to extract text from.
        
    Returns:
        Extracted text as a single string.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

