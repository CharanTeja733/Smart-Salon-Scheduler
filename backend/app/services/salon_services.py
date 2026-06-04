from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.repositories.salon_repository import SalonRepository
from app.services.google_places_service import GooglePlacesService
from app.models.salon import Salon
from app.config import settings

class SalonService:
    CACHE_TTL_DAYS = 7  # from settings.SALON_CACHE_TTL_SECONDS // 86400

    @staticmethod
    async def search_salons(
        lat: float,
        lng: float,
        radius: int,
        min_rating: float,
        limit: int,
        offset: int,
        db: Session
    ) -> Tuple[List[Salon], Optional[str]]:
        """
        Returns (list_of_salon_orm_objects, warning_message).
        warning_message is None if data is fresh from Google or cache.
        """
        repo = SalonRepository()

        # 1. Query DB once – store result
        cached_salons, is_fresh = repo.get_cached_by_location(
            db, lat, lng, radius, max_age_days=SalonService.CACHE_TTL_DAYS
        )

        # 2. If fresh, return directly
        if is_fresh and cached_salons:
            filtered = [s for s in cached_salons if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            return paginated, None

        # 3. No fresh data -> call Google API
        google_results = await GooglePlacesService.search_nearby(lat, lng, radius)

        if google_results is not None:
            # Google succeeded (results could be empty list)
            GooglePlacesService.store_results(db, google_results, lat, lng, radius)
            # Fetch fresh stored data (including potential zero-result marker)
            fresh_salons, _ = repo.get_cached_by_location(db, lat, lng, radius, max_age_days=0)
            filtered = [s for s in fresh_salons if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            return paginated, None

        # 4. Google failed (timeout/error). Use stale cached_salons if available.
        if cached_salons:
            filtered = [s for s in cached_salons if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            warning = "Using stale data. Google Places API temporarily unavailable."
            return paginated, warning

        # 5. No data at all – return empty list with error warning
        return [], "Unable to fetch salon data. Please try again later."