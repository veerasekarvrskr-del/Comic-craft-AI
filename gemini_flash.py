"""Gemini Flash - structured 5-panel comic outline generation."""
import json
import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FLASH_MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")

REQUIRED_KEYS = ("panel", "title", "scene_description", "image_prompt")


def generate_outline(user_prompt: str) -> list:
    prompt = f"""
You are a professional comic planner.

Your task is to generate a "strictly formatted" JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel": (integer)
- "title": (string)
- "scene_description": "scene description here",
- "image_prompt": "image prompt for Stable Diffusion"

Respond ONLY in this valid JSON format, without any explanations or markdown:

[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  ...
]
"""
    output_text = ""
    try:
        response = client.models.generate_content(model=FLASH_MODEL_NAME, contents=prompt)
        output_text = response.text.strip()

        if output_text.startswith("```"):
            output_text = output_text.replace("```json", "").replace("```", "").strip()

        panel_data = json.loads(output_text)

        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in REQUIRED_KEYS):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        return [{"error": f"JSON parsing failed: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Generation failed: {str(e)}"}]