import os
from datetime import datetime
from fpdf import FPDF


# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_FOLDER = os.path.join(BASE_DIR, "static", "exports")

FONT_PATH = os.path.join(
    BASE_DIR,
    "fonts"
)


# Make sure the export directory exists
os.makedirs(EXPORT_FOLDER, exist_ok=True)


def save_pdf(layout):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "", 12)

    for panel in layout:
        image_path = panel["image_path"]
        story_text = panel["text"]

        pdf.add_page()

        # Panel title
        pdf.set_font("Helvetica", "", 14)
        pdf.cell(
            0,
            10,
            f"Panel {panel['panel']}",
            ln=True,
            align="C"
        )

        pdf.set_font("Helvetica", "", 12)

        # Image placement
        y_image = 30
        image_height = 100
        spacing_after_image = 15

        if os.path.exists(image_path):
            pdf.image(
                image_path,
                x=10,
                y=y_image,
                w=pdf.w - 20,
                h=image_height
            )
        else:
            pdf.set_y(y_image)

            pdf.multi_cell(
                0,
                10,
                f"Image missing: {image_path}"
            )

        # Text placement below image
        pdf.set_y(
            y_image +
            image_height +
            spacing_after_image
        )

        story_lines = story_text.strip().splitlines()

        # Remove title line like **Panel 1: Title**
        if (
            story_lines
            and story_lines[0].lower().startswith("**panel")
        ):
            story_lines = story_lines[1:]

        cleaned_text = "\n".join(
            story_lines
        ).strip()

        pdf.multi_cell(
            0,
            10,
            cleaned_text
        )

    # Save with timestamp
    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    filename = f"comic_{timestamp}.pdf"

    filepath = os.path.join(
        EXPORT_FOLDER,
        filename
    )

    pdf.output(filepath)

    return filepath