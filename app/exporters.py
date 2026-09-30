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

# Unicode font
REGULAR_FONT = os.path.join(
    FONT_PATH,
    "DejaVuSans.ttf"
)

BOLD_FONT = os.path.join(
    FONT_PATH,
    "DejaVuSans-Bold.ttf"
)


# Make sure the export directory exists
os.makedirs(EXPORT_FOLDER, exist_ok=True)


def sanitize_text(text: str) -> str:
    """
    Replace common Unicode characters that may cause PDF encoding issues.
    """
    replacements = {
        "\u2014": "-",     # em dash
        "\u2013": "-",     # en dash
        "\u2018": "'",     # left single quote
        "\u2019": "'",     # right single quote
        "\u201c": '"',     # left double quote
        "\u201d": '"',     # right double quote
        "\u2026": "...",   # ellipsis
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def save_pdf(layout):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use Unicode font if available
    if os.path.exists(REGULAR_FONT):
        pdf.add_font(
            "DejaVu",
            "",
            REGULAR_FONT
        )

        if os.path.exists(BOLD_FONT):
            pdf.add_font(
                "DejaVu",
                "B",
                BOLD_FONT
            )

        pdf.set_font("DejaVu", "", 12)

    else:
        # Fallback to Helvetica
        pdf.set_font("Helvetica", "", 12)

    for panel in layout:
        image_path = panel["image_path"]
        story_text = panel["text"]

        pdf.add_page()

        # Panel title
        if os.path.exists(REGULAR_FONT):
            pdf.set_font("DejaVu", "B", 14)
        else:
            pdf.set_font("Helvetica", "", 14)

        pdf.cell(
            0,
            10,
            sanitize_text(f"Panel {panel['panel']}"),
            ln=True,
            align="C"
        )

        if os.path.exists(REGULAR_FONT):
            pdf.set_font("DejaVu", "", 12)
        else:
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
                sanitize_text(
                    f"Image missing: {image_path}"
                )
            )

        # Text placement below image
        pdf.set_y(
            y_image +
            image_height +
            spacing_after_image
        )

        cleaned_text = sanitize_text(
            story_text.strip()
        )

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