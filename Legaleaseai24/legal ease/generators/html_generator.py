from html import escape


def format_html_preview(document: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in document.split("\n\n") if paragraph.strip()]
    return "".join(f"<p>{escape(paragraph).replace(chr(10), '<br>')}</p>" for paragraph in paragraphs)
