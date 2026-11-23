from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfminer.pdfparser import PDFSyntaxError

from app.auth.dependencies import get_current_user
from app.core.mongodb import MongoDB
from app.services.holiday_service import parse_holiday_pdf

router = APIRouter()
HOLIDAY_COLLECTION = "yearly_holiday"
MAX_PDF_SIZE = 10 * 1024 * 1024


@router.get("")
async def get_holidays(
    year: int | None = Query(default=None),
    _: dict = Depends(get_current_user),
) -> list[dict[str, Any]]:
    collection = MongoDB.get_collection(HOLIDAY_COLLECTION)
    selected_year = year if year is not None else date.today().year
    records = await collection.find({"year": selected_year}, {"_id": 0}).sort("date", 1).to_list(length=None)
    return records


@router.post("/import")
async def import_holidays(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    contents = await file.read(MAX_PDF_SIZE + 1)
    if len(contents) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="PDF file exceeds the 10 MB limit.")
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    try:
        holidays = parse_holiday_pdf(contents)
    except (OSError, PDFPasswordIncorrect, PDFSyntaxError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Unable to extract holidays from PDF: {exc}") from exc

    collection = MongoDB.get_collection(HOLIDAY_COLLECTION)
    years = sorted({holiday["year"] for holiday in holidays})
    for year in years:
        await collection.delete_many({"year": year})
    await collection.insert_many(holidays)

    return {
        "message": f"Imported {len(holidays)} holidays.",
        "count": len(holidays),
        "years": years,
    }
