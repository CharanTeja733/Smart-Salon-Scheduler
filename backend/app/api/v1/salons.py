from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.google_places_service import GooglePlacesService
from app.repositories.salon_repository import SalonRepository
from app.schemas.salon import SalonResponse, SalonSearchParams

router = APIRouter()

@router.get("/", response_model=List[SalonResponse])
async def search_salons(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(5000, ge=100, le=50000),
    min_rating: float = Query(0.0, ge=0, le=5),
    service_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    # Try Google Places API first (refresh cache if stale)
    # For simplicity, we first return cached results, then optionally refresh async
    salon_repo = SalonRepository()
    salons = salon_repo.search_by_location(db, lat, lng, radius, min_rating, limit, offset)
    
    # If no results or cache is old, trigger background refresh (optional)
    if not salons:
        # Fallback to Google Places (synchronous for simplicity)
        await GooglePlacesService.fetch_and_cache_salons(db, lat, lng, radius)
        salons = salon_repo.search_by_location(db, lat, lng, radius, min_rating, limit, offset)
    
    return salons

@router.get("/{salon_id}", response_model=SalonResponse)
async def get_salon(
    salon_id: int,
    db: Session = Depends(get_db)
):
    salon_repo = SalonRepository()
    salon = salon_repo.get_by_id(db, salon_id)
    if not salon:
        raise HTTPException(status_code=404, detail="Salon not found")
    return salon