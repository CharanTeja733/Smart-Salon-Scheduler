# backend/app/api/v1/salons.py
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.salon_service import SalonService
from app.schemas.salon import SalonResponse

router = APIRouter()

@router.get("/", response_model=List[SalonResponse])
async def search_salons(
    response: Response,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(5000, ge=100, le=50000),
    min_rating: float = Query(0.0, ge=0, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    salons, warning = await SalonService.search_salons(
        lat, lng, radius, min_rating, limit, offset, db
    )

    if warning and "Unable to fetch" in warning:
        # If no data and Google failed, return 503
        response.status_code = 503
        # The response model will still be applied, but we return empty list.
        # Alternatively, you can raise an HTTPException.
        # For simplicity, we set status code and return empty list.
    if warning:
        response.headers["X-Cache-Warning"] = warning

    return salons