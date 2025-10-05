# step1: install tectonic and import dependencies
import os
from langchain_core.tools import tool
from datetime import datetime
import subprocess
from pathlib import Path
import shutil

@tool
def render_latex_pdf(latex_content: str) -> str:
    """Render a LaTeX document to PDF.

    Args:
        latex_content: The LaTeX document content as a string

    Returns:
        Path to the generated PDF document
    """
    if shutil.which("tectonic") is None:
        raise RuntimeError(
            "tectonic is not installed. Install it first on your system."
        )
    try:     
        # step2: create directory if not exists
        OUTPUT_DIR = "output_pdfs"
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        # step3: setup the filename with timestamp
        def get_timestamped_filename():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            tex_filename = f"Paper_{timestamp}.tex"
            pdf_filename = f"Paper_{timestamp}.pdf"
            return tex_filename, pdf_filename

        tex_filename, pdf_filename = get_timestamped_filename()

        # step4: Export as tex
        tex_file = Path(OUTPUT_DIR) / tex_filename
        tex_file.write_text(latex_content, encoding="utf-8")

        # step5: Compile to PDF using tectonic
        result = subprocess.run(
            ["tectonic", str(tex_file), "--outdir", OUTPUT_DIR],
            check=True,
        )

        final_pdf = Path(OUTPUT_DIR) / pdf_filename
        if not final_pdf.exists():
            raise FileNotFoundError("PDF file was not generated")
        
        print(f"Successfully generated PDF at {final_pdf}")
        return str(final_pdf)
    except Exception as e:
        print(f"Error rendering LaTex: {str(e)}")
        raise
