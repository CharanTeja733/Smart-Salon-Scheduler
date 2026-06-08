# backend/app/services/salon_service.py
import math
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.salon import Salon
from app.repositories.salon import SalonRepository
from app.services.google_places import GooglePlacesService

class SalonService:
    CACHE_TTL_DAYS = 7

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Return distance in meters between two points using Haversine formula."""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c * 1000  # meters

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
        repo = SalonRepository()

        # 1. Get cached salons (pure ORM objects, no distance)
        cached_salons, is_fresh = repo.get_cached_by_location(
            db, lat, lng, radius, max_age_days=SalonService.CACHE_TTL_DAYS
        )

        # Helper to compute distance for a list of salons
        def add_distances(salons: List[Salon]) -> List[Salon]:
            for s in salons:
                s.distance_meters = round(SalonService.haversine(lat, lng, s.latitude, s.longitude), 1)
            return salons

        # 2. Return fresh data
        if is_fresh and cached_salons:
            salons_with_dist = add_distances(cached_salons)
            filtered = [s for s in salons_with_dist if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            return paginated, None

        # 3. No fresh data -> call Google Places
        google_results = await GooglePlacesService.search_nearby(lat, lng, radius)

        if google_results is not None:
            await GooglePlacesService.store_results(db, google_results, lat, lng, radius)
            # Fetch newly stored salons (with max_age_days=0 to force refresh)
            fresh_salons, _ = repo.get_cached_by_location(db, lat, lng, radius, max_age_days=0)
            fresh_with_dist = add_distances(fresh_salons)
            filtered = [s for s in fresh_with_dist if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            return paginated, None

        # 4. Google failed, use stale data if available
        if cached_salons:
            stale_with_dist = add_distances(cached_salons)
            filtered = [s for s in stale_with_dist if s.rating >= min_rating]
            paginated = filtered[offset:offset+limit]
            return paginated, "Using stale data. Google Places API temporarily unavailable."

        # 5. No data at all
        return [], "Unable to fetch salon data. Please try again later."