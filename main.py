"""ComicCraft - AI Comic Story Creator (FastAPI entry point).

Run from the project root:
    uvicorn app.main:app --reload
"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Make sure output folders exist before the app starts
os.makedirs(os.path.join(STATIC_DIR, "panels"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "exports"), exist_ok=True)

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate comic stories and illustrations with Gemini + Stable Diffusion.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)
