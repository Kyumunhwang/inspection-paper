"""Document parser API router for Google Docs inspection and metadata extraction."""

from fastapi import APIRouter, HTTPException
from app.services.parser_service import parser_service

router = APIRouter(prefix="/api/parser", tags=["Document Parsing"])


@router.get("/doc/{doc_id}")
def get_parsed_doc(doc_id: str) -> dict:
    """Retrieve full parsed data, raw stream, and heuristics for a document."""
    doc = parser_service.get_parsed_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@router.post("/doc/{doc_id}/reparse")
def reparse_doc(doc_id: str) -> dict:
    """Trigger re-parsing of document from Google Docs stream."""
    try:
        return parser_service.reparse_document(doc_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
