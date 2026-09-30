"""All FastAPI routes for ComicCraft."""
import os
import re

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape
from pydantic import BaseModel

from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _format_text(value: str) -> Markup:
    """Jinja filter: escape the text, then turn **bold** markers into <strong>."""
    safe = str(escape(value or ""))
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    return Markup(safe.replace("\n", "<br>"))


templates.env.filters["format_text"] = _format_text


class PromptRequest(BaseModel):
    """JSON body for /generate-comic/json"""
    prompt: str
    character_name: str = "Hero"
    setting: str = "forest"
    tone: str = "dramatic"
    style: str = "comic book"


def _combine_prompt(prompt: str, character_name: str, setting: str, tone: str, style: str) -> str:
    """Combine all user input into a single story prompt."""
    return (
        f"{prompt}\n"
        f"The main character is {character_name}.\n"
        f"The setting is in {setting}.\n"
        f"The tone is {tone}.\n"
        f"The art style is {style}."
    )


def _run_pipeline(prompt: str, character_name: str, setting: str, tone: str, style: str):
    """outline -> story -> images -> layout -> PDF. Returns (layout, pdf_path)."""
    full_prompt = _combine_prompt(prompt, character_name, setting, tone, style)

    # Step 1: Generate panel outline
    outline = generate_outline(full_prompt)
    if not isinstance(outline, list) or not all(
        isinstance(p, dict) and "image_prompt" in p for p in outline
    ):
        detail = "Invalid outline structure from Gemini response."
        if isinstance(outline, list) and outline and isinstance(outline[0], dict) and "error" in outline[0]:
            detail = f"{detail} {outline[0]['error']}"
        raise HTTPException(status_code=500, detail=detail)

    # Step 2: Generate story
    full_story = generate_story(outline)

    # Step 3: Generate images (art style is added to every image prompt)
    images = [
        generate_image(f"{panel['image_prompt']}, {style} style")
        for panel in outline
    ]

    # Step 4: Build layout
    layout = build_comic_layout(images, full_story, outline)

    # Step 5: Export to PDF
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/generate", response_class=HTMLResponse)
def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    try:
        layout, pdf_path = _run_pipeline(prompt, character_name, setting, tone, style)
        return templates.TemplateResponse(
            request,
            "comic_preview.html",
            {"layout": layout, "pdf_path": pdf_path},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-comic/json")
def generate_comic_json(data: PromptRequest):
    try:
        layout, pdf_path = _run_pipeline(
            data.prompt, data.character_name, data.setting, data.tone, data.style
        )
        return {"layout": layout, "pdf_path": pdf_path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request,
        "export_success.html",
        {"pdf_path": pdf_path},
    )


@router.get("/test-image")
def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artistic"):
    """Developer utility: test image generation without creating a full comic."""
    try:
        image_path = generate_image(prompt)
        return {"message": "Image generated successfully", "path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
