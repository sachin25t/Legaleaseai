from io import BytesIO

from fpdf import FPDF


class _DocumentPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)


def format_pdf(document: str, document_type: str, logo_file=None) -> bytes:
    pdf = _DocumentPDF()
    pdf.title = document_type or "LegalEase Document"
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    if logo_file is not None:
        try:
            logo_file.seek(0)
            image_path = getattr(logo_file, "name", None)
            if image_path:
                pdf.image(image_path, w=35)
                pdf.ln(5)
        except Exception:
            pass

    for paragraph in document.split("\n\n"):
        if paragraph.strip():
            pdf.multi_cell(0, 7, paragraph.strip())
            pdf.ln(3)

    return bytes(pdf.output())
