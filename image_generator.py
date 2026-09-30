"""Stable Diffusion - comic-style panel illustration generation."""
import os
import re
import uuid

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS_DIR = os.path.join(BASE_DIR, "static", "panels")

SD_MODEL_ID = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
HF_TOKEN = os.getenv("HF_API_KEY")

_pipe = None  # loaded lazily so the server starts quickly


def _get_pipeline():
    """Load the Stable Diffusion pipeline once, on first use (GPU if available)."""
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        kwargs = {"torch_dtype": dtype}
        if HF_TOKEN:
            kwargs["token"] = HF_TOKEN
        pipe = StableDiffusionPipeline.from_pretrained(SD_MODEL_ID, **kwargs)
        _pipe = pipe.to(device)
    return _pipe


def sanitize_filename(text: str, max_length: int = 40) -> str:
    """Turn a prompt into a safe, unique filename (without extension)."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()[:max_length] or "panel"
    return f"{cleaned}_{uuid.uuid4().hex[:8]}"


def generate_image(prompt: str, filename: str = None) -> str:
    """
    Generate a comic-style image from a prompt and save it in static/panels.

    Returns:
        str: web-relative path of the saved image, e.g. "static/panels/fox_ab12cd34.png"
    """
    if not filename:
        filename = sanitize_filename(prompt)
    if not filename.lower().endswith(".png"):
        filename += ".png"

    pipe = _get_pipeline()
    image = pipe(prompt).images[0]

    os.makedirs(PANELS_DIR, exist_ok=True)
    image.save(os.path.join(PANELS_DIR, filename))
    return f"static/panels/{filename}"
