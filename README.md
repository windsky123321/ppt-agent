# Personalized Paper-to-PPT Agent

Local-first web app for turning an academic paper PDF into an editable PowerPoint deck, with grounded intermediate artifacts, persistent user profiles, multimodal asset extraction, critic/repair checks, and selected-slide regeneration.

## Current Status

The project now supports:

- PDF upload and parsing
- grounded paper summary
- profile-aware deck planning
- grounded slide drafting
- figure/table asset extraction
- grounding report
- critic report
- deterministic repair loop
- editable PPTX generation
- selected-slide regeneration
- local JSON artifact storage
- mock mode without paid API keys

## Stack

- Backend: Python 3.11+, FastAPI, Pydantic, PyMuPDF, python-pptx, Pillow
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Storage: local filesystem JSON artifacts, no database

## Project Structure

```text
backend/
  app/
    main.py
    config.py
    api/
    schemas/
    parser/
    agents/
    llm/
    ppt/
    storage/
    prompts/
    utils/
    vision/
  scripts/
  tests/
frontend/
  src/
    components/
    pages/
    api/
    types/
    stores/
examples/
.env.example
README.md
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

If PowerShell blocks `npm`, use `npm.cmd`.

## Environment Variables

Copy `.env.example` to `.env`.

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
DEFAULT_LLM_PROVIDER=mock
STORAGE_DIR=./storage
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_API_BASE_URL=http://127.0.0.1:8000
ENABLE_CRITIC=true
ENABLE_REPAIR=true
MAX_REPAIR_LOOPS=2
```

## Profiles

Profiles are stored locally as JSON and can be managed through:

- `POST /api/profiles`
- `GET /api/profiles`
- `GET /api/profiles/{profile_id}`
- `PUT /api/profiles/{profile_id}`
- `DELETE /api/profiles/{profile_id}`

Built-in presets:

- Chinese Graduate Reading Group
- English Expert Conference Talk
- Bilingual Undergraduate Teaching
- Critical Review Lab Meeting

Profiles affect:

- deck length
- language
- tone
- math depth
- notes
- limitations / discussion inclusion
- source footers
- theme and density

## API

- `POST /api/papers/upload`
- `GET /api/jobs/{job_id}`
- `GET /api/decks/{deck_id}/download`
- `GET /api/decks/{deck_id}/artifacts`
- `GET /api/decks/{deck_id}/artifacts/{artifact_name}`
- `POST /api/decks/{deck_id}/regenerate-slide`
- `GET /api/profiles`
- `POST /api/profiles`
- `GET /api/profiles/{profile_id}`
- `PUT /api/profiles/{profile_id}`
- `DELETE /api/profiles/{profile_id}`
- `GET /api/health`

## Multimodal Assets

Figures and tables are extracted into structured asset objects and saved as:

- `extracted_assets.json`

Each asset includes:

- type
- page number
- caption
- nearby text
- optional image path
- short visual description
- technical interpretation
- why it matters
- suggested slide usage
- importance score
- source reference

Mock vision mode works without external APIs.

Vision analysis with a real provider is not fully implemented yet; mock mode falls back to caption and nearby text heuristics.

## Grounding, Critic, and Repair

The system saves:

- `grounding_report.json`
- `critic_report.json`
- `repair_history.json`

The critic checks:

- unsupported claims
- weak grounding
- missing source refs
- abstract-only refs
- too many bullets
- dense text
- weak notes
- low confidence
- likely overflow
- poor visual usage

The repair loop:

- only modifies affected slides when possible
- does not reparse the whole paper
- can add notes, trim bullets, add conservative refs, and attach useful assets
- is capped by `MAX_REPAIR_LOOPS`

## Selected-Slide Regeneration

Use:

- `POST /api/decks/{deck_id}/regenerate-slide`

Request body:

```json
{
  "slide_ids": ["slide_05"],
  "instruction": "Make this slide more visual and reduce text.",
  "profile_id": "optional"
}
```

This updates only the requested slides, re-runs grounding and critic checks, and rebuilds the PPTX.

## Artifact Output

Each generation job may store:

- `original.pdf`
- `parsed_paper.json`
- `extracted_assets.json`
- `paper_summary.json`
- `deck_plan.json`
- `slide_drafts.json`
- `grounding_report.json`
- `critic_report.json`
- `repair_history.json`
- `final_deck.pptx`
- `job_status.json`

## Mock Mode

The app works with `DEFAULT_LLM_PROVIDER=mock` and requires no paid API key.

Mock mode supports:

- profile-based generation
- mock figure/table understanding
- deterministic asset ranking
- grounding checks
- critic and repair loop
- selected-slide regeneration
- PPTX generation

## Smoke Tests

Round 1 smoke:

```bash
cd backend
python scripts/smoke_test.py
```

Round 2 smoke:

```bash
cd backend
python scripts/smoke_round2.py
```

## Tests

```bash
cd backend
pytest
```

Covered areas:

- parser
- summary / deck / slide schemas
- profile CRUD and validation
- profile-driven planning
- mock vision model
- asset ranking
- grounding checker
- critic JSON behavior
- repair loop
- selected-slide regeneration
- upload API
- PPTX generation

## Frontend Round 2 UX

The frontend exposes:

- backend connection via API usage
- upload area
- selected PDF
- profile selector
- profile editor
- generation settings
- stage/status panel
- artifact list
- critic warnings
- grounding warnings
- selected-slide regeneration controls
- PPTX download

## Example Workflow

1. Start backend.
2. Start frontend.
3. Select or edit a profile.
4. Upload a paper PDF.
5. Generate the deck.
6. Inspect artifacts and warnings.
7. Regenerate weak slides if needed.
8. Download `final_deck.pptx`.

## Troubleshooting

- If no figures are extracted, the deck still falls back to text-grounded slides.
- If the vision model is unavailable, mock asset descriptions use captions and nearby text.
- If unsupported claims are detected, they are removed or flagged.
- If critic approval is false, inspect `critic_report.json` and `grounding_report.json`.
- Multi-column PDFs may still produce noisy section extraction.

## Limitations

- Multi-column PDF parsing is still noisy on some papers.
- Figure/table extraction is heuristic and not yet bbox-precise.
- Scientific figures are not fully interpreted without a stronger vision provider.
- Asset image export is still lightweight and may fall back to text-only usage.
- Some source refs remain conservative when explicit section evidence is limited.
- Generated slides should still be reviewed by humans before important use.

## Safety Notes

- Vision analysis requires a configured vision provider unless using mock mode.
- Generated slides should still be reviewed by humans.
- Unsupported paper claims are removed or flagged where detected.
- Multi-column PDFs may still produce noisy section extraction.
