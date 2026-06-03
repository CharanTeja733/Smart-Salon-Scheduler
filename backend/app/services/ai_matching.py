from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories import PractitionerRepository, CustomerRepository, AppointmentRepository, ReviewRepository
from app.services.scheduling_service import SchedulingService
from app.services.sentiment_service import SentimentService
from math import radians, sin, cos, sqrt, atan2

class AIStylistMatcherService:
    WEIGHTS = {
        "expertise": 0.40,
        "rating": 0.25,
        "sentiment": 0.15,
        "workload": 0.10,
        "distance": 0.10
    }

    @staticmethod
    async def find_best_matches(
        service_type: str,
        db: Session,
        customer_phone: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        preferred_date=None,
        limit: int = 3
    ) -> List[Dict]:
        practitioner_repo = PractitionerRepository()
        customer_repo = CustomerRepository()
        appointment_repo = AppointmentRepository()
        review_repo = ReviewRepository()

        # Get all practitioners offering this service
        practitioners = practitioner_repo.get_by_service_type(db, service_type)

        # Customer preferences (if exists)
        customer = None
        if customer_phone:
            customer = customer_repo.get_by_phone(db, customer_phone)

        scored = []
        for p in practitioners:
            score = 0.0
            breakdown = {}

            # 1. Expertise match (40%)
            expertise_score = 100.0 if service_type in (p.specializations or []) else 50.0
            breakdown["expertise_match"] = expertise_score
            score += expertise_score * AIStylistMatcherService.WEIGHTS["expertise"]

            # 2. Rating (25%)
            rating_score = (p.rating / 5.0) * 100
            breakdown["rating"] = rating_score
            score += rating_score * AIStylistMatcherService.WEIGHTS["rating"]

            # 3. Review sentiment (15%)
            reviews = review_repo.get_by_practitioner(db, p.id, limit=50)
            if reviews:
                avg_sentiment = sum(r.sentiment_score or 0.5 for r in reviews) / len(reviews)
            else:
                avg_sentiment = 0.5
            sentiment_score = ((avg_sentiment + 1) / 2) * 100  # -1..1 to 0..100
            breakdown["sentiment"] = sentiment_score
            score += sentiment_score * AIStylistMatcherService.WEIGHTS["sentiment"]

            # 4. Workload balance (10%)
            upcoming = appointment_repo.get_upcoming_for_customer(db, p.id, limit=100)
            workload_score = max(0, 100 - (len(upcoming) * 2))  # penalize many upcoming
            breakdown["workload"] = workload_score
            score += workload_score * AIStylistMatcherService.WEIGHTS["workload"]

            # 5. Distance (10%) if coordinates provided
            distance_score = 100.0
            if lat and lng and p.salon:
                dist = AIStylistMatcherService._haversine(lat, lng, p.salon.latitude, p.salon.longitude)
                # Normalize: 0km = 100, 10km = 0
                distance_score = max(0, 100 - (dist / 0.1))
                breakdown["distance"] = distance_score
                score += distance_score * AIStylistMatcherService.WEIGHTS["distance"]

            scored.append({
                "practitioner": p,
                "score": round(score, 1),
                "breakdown": breakdown
            })

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)

        # Build response with availability for preferred date
        result = []
        for item in scored[:limit]:
            p = item["practitioner"]
            slots = []
            if preferred_date:
                slots = SchedulingService.generate_available_slots(p.id, preferred_date, db)
            result.append({
                "practitioner_id": p.id,
                "name": p.name,
                "salon_name": p.salon.name if p.salon else "",
                "rating": p.rating,
                "price": p.service_prices.get(service_type, p.base_price),
                "available_slots": [s.isoformat() for s in slots],
                "match_score": item["score"],
                "match_breakdown": item["breakdown"],
                "explanation": AIStylistMatcherService._generate_explanation(item["breakdown"])
            })
        return result

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    @staticmethod
    def _generate_explanation(breakdown: dict) -> str:
        parts = []
        if breakdown["expertise_match"] > 80:
            parts.append("perfect match for your service")
        if breakdown["rating"] > 90:
            parts.append("highly rated by customers")
        if breakdown["sentiment"] > 70:
            parts.append("excellent reviews")
        return f"{', '.join(parts)}." if parts else "Good overall match."