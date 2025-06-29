from fastapi import APIRouter, UploadFile, File
from unstructured.partition.docx import partition_docx

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("")
async def ingest(file: UploadFile = File(...)):
    chunks = partition_docx(file.file)
    spec = {c.metadata.section_title or f"sec_{i}": {"raw": c.text, "status": "🔴"} for i, c in enumerate(chunks)}
    return spec