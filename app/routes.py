from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import traceback

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf
import os


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    try:
        # Combine user input into a single prompt
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}. "
            f"The setting is a {setting}. "
            f"The tone is {tone}. "
            f"The art style is {style}."
        )

        # Step 1: Generate panel outline using Gemini Flash
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or not all(
            isinstance(panel, dict) and "image_prompt" in panel
            for panel in outline
        ):
            raise ValueError(
                "Invalid outline structure from Gemini response."
            )

        # Step 2: Generate comic story using Gemini Pro
        story_panels = generate_story(outline)

        # Step 3: Generate images using Hugging Face
        images = [
            generate_image(panel["image_prompt"])
            for panel in outline
        ]

        # Step 4: Build comic layout
        layout = build_comic_layout(
            images,
            story_panels,
            outline
        )

        # Step 5: Export comic to PDF
        pdf_path = save_pdf(layout)

        filename = os.path.basename(pdf_path)

        web_pdf_path = f"/static/exports/{filename}"

        return templates.TemplateResponse(
            request=request,
            name="export_success.html",
            context={
                "request": request,
                "pdf_path": web_pdf_path
            }
        )

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    pdf_path: str
):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request, 
            "pdf_path": pdf_path
            }
    )


@router.get("/test-image")
async def test_image(
    prompt: str = "A futuristic city at sunset, sci-fi, cinematic, comic book art"
):
    try:
        image_path = generate_image(prompt)

        return {
            "message": "Image generated successfully",
            "path": image_path
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )