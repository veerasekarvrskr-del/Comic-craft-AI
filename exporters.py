"""Export the finished comic to a multi-page PDF using FPDF."""
import os
from datetime import datetime

from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, "static", "fonts")
EXPORT_FOLDER = os.path.join(BASE_DIR, "static", "exports")


def _clean(text: str) -> str:
    """Remove the ** markdown markers so the PDF reads cleanly."""
    return (text or "").replace("**", "").strip()


def save_pdf(layout: list) -> str:
    """
    Compile the comic layout into a PDF (one panel per page).

    Returns:
        str: web-relative path of the PDF, e.g. "static/exports/comic_20260928_101500.pdf"
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Unicode font so quotes, dashes and non-English text do not crash the export
    pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"), uni=True)
    pdf.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), uni=True)
    pdf.add_font("DejaVu", "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"), uni=True)

    for panel in layout:
        pdf.add_page()

        # Panel title
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 10, f"Panel {panel['panel']}: {_clean(panel.get('title', ''))}", ln=True, align="L")

        # Image placement
        y_image = 30
        image_height = 100
        image_abs = os.path.join(BASE_DIR, panel["image_path"])
        if os.path.exists(image_abs):
            pdf.image(image_abs, x=30, y=y_image, w=pdf.w - 60, h=image_height)
        else:
            pdf.set_y(y_image)
            pdf.set_font("DejaVu", "", 12)
            pdf.multi_cell(0, 10, f"Image missing: {panel['image_path']}")
        pdf.set_y(y_image + image_height + 5)

        # Scene description (italic)
        scene = _clean(panel.get("scene_description", ""))
        if scene:
            pdf.set_font("DejaVu", "I", 11)
            pdf.multi_cell(0, 7, scene)
            pdf.ln(2)

        # Caption / narration text
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, _clean(panel.get("text", "")))

    # Save with timestamp
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf.output(os.path.join(EXPORT_FOLDER, filename))
    return f"static/exports/{filename}"
