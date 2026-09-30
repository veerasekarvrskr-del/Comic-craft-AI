"""Organise generated images and story text into a per-panel layout."""
import re

_HEADING = re.compile(r"\*{0,2}\s*Panel\s*\d+\s*[:\-.]?", re.IGNORECASE)


def _split_story(full_story: str) -> list:
    """Split the full story into one text block per panel."""
    parts = _HEADING.split(full_story)
    # anything before the first "Panel N" heading is an introduction
    if len(parts) > 1:
        parts = parts[1:]
    return [p.strip() for p in parts if p.strip()]


def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Match every image with its panel story.

    Returns:
        list[dict]: panel number, title, image_path, text, scene_description
    """
    story_panels = _split_story(full_story or "")

    layout = []
    for idx, (image_path, panel_info) in enumerate(zip(image_paths, outline), start=1):
        text = ""
        if idx - 1 < len(story_panels):
            lines = story_panels[idx - 1].splitlines()
            # first line is the rest of the heading (the panel title) - drop it
            text = "\n".join(lines[1:]).strip() if len(lines) > 1 else story_panels[idx - 1]
        if not text:
            text = panel_info.get("scene_description", "")

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image_path,
            "text": text,
            "scene_description": panel_info.get("scene_description", ""),
        })
    return layout
