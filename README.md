# ComicCraft - AI Comic Story Creator using Gemini Models

ComicCraft is a FastAPI web app that turns a story prompt (plus character name, setting, tone and art style)
into a 5-panel comic: **Gemini Flash** plans the panels, **Gemini Pro** writes narration and dialogue,
**Stable Diffusion** (Hugging Face Diffusers) draws each panel, and **FPDF** exports the comic as a PDF.

## Project structure
```
comiccraft/
├── app/
│   ├── main.py              # FastAPI app, static files, router
│   ├── routes.py            # /, /generate, /generate-comic/json, /export-success, /test-image
│   ├── gemini_flash.py      # generate_outline()
│   ├── gemini_pro.py        # generate_story()
│   ├── image_generator.py   # generate_image()
│   ├── layout_builder.py    # build_comic_layout()
│   └── exporters.py         # save_pdf()
├── templates/               # index.html, comic_preview.html, export_success.html
├── static/                  # panels/ (images), exports/ (PDFs), fonts/, images/
├── .env.example             # copy to .env and add your keys
└── requirements.txt
```

## Setup
```bash
python -m venv env
env\Scripts\activate            # Windows
# source env/bin/activate       # macOS / Linux
pip install -r requirements.txt
copy .env.example .env          # (cp on macOS/Linux) then edit .env with your keys
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 for the app and http://127.0.0.1:8000/docs for API testing.

## Environment variables (`.env`)
| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `HF_API_KEY` | Hugging Face token (used when downloading the model) |
| `GEMINI_FLASH_MODEL` / `GEMINI_PRO_MODEL` | optional model overrides (defaults `models/gemini-1.5-flash`, `models/gemini-1.5-pro`) |
| `SD_MODEL_ID` | optional Stable Diffusion override (default `runwayml/stable-diffusion-v1-5`) |

**Note:** Google has retired the Gemini 1.5 models and the original `runwayml/stable-diffusion-v1-5` repo has moved.
If you get a "model not found" error, set newer values in `.env`, e.g. `GEMINI_FLASH_MODEL=models/gemini-2.5-flash`,
`GEMINI_PRO_MODEL=models/gemini-2.5-pro` and `SD_MODEL_ID=stable-diffusion-v1-5/stable-diffusion-v1-5`.
A GPU is strongly recommended; on CPU each panel image can take several minutes.

## Routes
| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page with the input form |
| `/generate` | POST | Form submission -> full comic preview page |
| `/generate-comic/json` | POST | Same pipeline via JSON (`prompt`, `character_name`, `setting`, `tone`, `style`); returns layout + PDF path |
| `/export-success` | GET | Confirmation page after PDF download |
| `/test-image` | GET | Generate one image from `?prompt=` for testing |
