import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
CATALOG_FILE = Path(__file__).parent.parent.parent / "catalog.json"

SLUG_TO_FILE: dict[str, str] = {
    "mutual-non-disclosure-agreement": "Mutual-NDA.md",
    "mutual-nda-cover-page": "Mutual-NDA-coverpage.md",
    "cloud-service-agreement": "CSA.md",
    "design-partner-agreement": "design-partner-agreement.md",
    "service-level-agreement": "sla.md",
    "professional-services-agreement": "psa.md",
    "data-processing-agreement": "DPA.md",
    "software-license-agreement": "Software-License-Agreement.md",
    "partnership-agreement": "Partnership-Agreement.md",
    "pilot-agreement": "Pilot-Agreement.md",
    "business-associate-agreement": "BAA.md",
    "ai-addendum": "AI-Addendum.md",
}


@router.get("/")
async def list_templates():
    with open(CATALOG_FILE) as f:
        catalog = json.load(f)
    return catalog


@router.get("/{slug}/content", response_class=PlainTextResponse)
async def get_template_content(slug: str):
    filename = SLUG_TO_FILE.get(slug)
    if not filename:
        raise HTTPException(status_code=404, detail=f"Unknown document type: {slug}")
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template file not found: {filename}")
    return path.read_text()
