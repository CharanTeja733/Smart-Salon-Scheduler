# backend/app/api/v1/salons.py
from typing import List

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.schemas.salon import SalonResponse
from app.services.salon import SalonService
from app.models.salon import Salon


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


@router.get("/{salon_id}", response_model=SalonResponse)
async def get_salon(
    salon_id: int,
    db: Session = Depends(get_db)
):
    salon = db.query(Salon).options(
        joinedload(Salon.practitioners)   # eager load all practitioners
    ).filter(Salon.id == salon_id).first()
    
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    
    return salon