from langchain_core.tools import tool
import os
import io
import PyPDF2
import requests

@tool
def read_pdf(file_path: str) -> str:
    """Read a PDF file and extract its text content.
    Args:
        file_path (str): The path to the PDF file.
    Returns:
        str: The extracted text content of the PDF.
    """
    try:
        response = requests.get(file_path)
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)
        text = ""
        for i,page in enumerate(reader.pages, start=1):
            print(f"Reading page {i}/{num_pages}")
            text += page.extract_text() + "\n"

        print(f"Extracted {len(text)} characters from the PDF.")
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return ""
    
print(read_pdf("https://arxiv.org/pdf/2305.10403.pdf"))