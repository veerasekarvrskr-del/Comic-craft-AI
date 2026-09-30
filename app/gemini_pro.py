"""Gemini Pro - detailed comic narration and character dialogue."""
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
PRO_MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")


def generate_story(outline: list) -> str:
    formatted_outline = "\n".join(f"{i+1}. {item}" for i, item in enumerate(outline))
    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
- Include narration and clearly marked character lines.
- Keep each panel self-contained but part of a cohesive story.
- Start every panel with a heading in exactly this form: **Panel N: Title**
- Under each heading write these three labelled parts:
  **CAPTION:** a short ambient line about the environment or sounds
  **NARRATION:** the main character's actions, emotions or dialogue
  **IMAGE PROMPT:** a one-line artistic description of the illustration
"""
    try:
        response = client.models.generate_content(model=PRO_MODEL_NAME, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"