"""AI Quality Evaluation API router following rules.md guidelines."""

from fastapi import APIRouter, HTTPException
from app.services.ai_service import ai_service
from app.services.parser_service import parser_service

router = APIRouter(prefix="/api/ai", tags=["AI Quality Audit"])


@router.post("/batch-audit")
def run_batch_quality_audit() -> dict:
    """Run full AI batch quality inspection on all current examination papers."""
    return ai_service.run_batch_audit()


@router.post("/audit/{doc_id}")
def audit_single_document(doc_id: str) -> dict:
    """Run AI evaluation on a specific document by ID."""
    doc = parser_service.get_parsed_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    raw_text = doc.get("rawText", "")
    subject = doc["metadata"]["subject"]
    return ai_service.evaluate_exam_text(raw_text, subject)
