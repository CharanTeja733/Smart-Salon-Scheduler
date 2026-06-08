from math import atan2, cos, radians, sin, sqrt
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.repositories import (
    AppointmentRepository,
    CustomerRepository,
    PractitionerRepository,
    ReviewRepository,
)
from app.services.scheduling import SchedulingService


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

        # Fetch customer if phone provided
        customer = None
        past_stylist_ids = set()
        if customer_phone:
            customer = customer_repo.get_by_phone(db, customer_phone)
            if customer:
                # Get list of stylist IDs this customer has booked before (completed appointments)
                past_appointments = appointment_repo.get_past_for_customer(db, customer.id, limit=100)
                past_stylist_ids = {apt.practitioner_id for apt in past_appointments}

        # Weight adjustments (total 100%)
        WEIGHTS = {
            "expertise": 0.35,
            "rating": 0.20,
            "sentiment": 0.15,
            "workload": 0.10,
            "distance": 0.10,
            "customer_preference": 0.10   # new factor
        }

        scored = []
        for p in practitioners:
            score = 0.0
            breakdown = {}

            # 1. Expertise match (35%)
            expertise_score = 100.0 if service_type in (p.specializations or []) else 50.0
            breakdown["expertise_match"] = expertise_score
            score += expertise_score * WEIGHTS["expertise"]

            # 2. Rating (20%)
            rating_score = (p.rating / 5.0) * 100
            breakdown["rating"] = rating_score
            score += rating_score * WEIGHTS["rating"]

            # 3. Review sentiment (15%)
            reviews = review_repo.get_by_practitioner(db, p.id, limit=50)
            if reviews:
                avg_sentiment = sum(r.sentiment_score or 0.5 for r in reviews) / len(reviews)
            else:
                avg_sentiment = 0.5
            sentiment_score = ((avg_sentiment + 1) / 2) * 100
            breakdown["review_sentiment"] = sentiment_score
            score += sentiment_score * WEIGHTS["sentiment"]

            # 4. Workload balance (10%)
            upcoming = appointment_repo.get_upcoming_for_customer(db, p.id, limit=100)
            workload_score = max(0, 100 - (len(upcoming) * 2))
            breakdown["workload_balance"] = workload_score
            score += workload_score * WEIGHTS["workload"]

            # 5. Distance (10%) if coordinates provided
            distance_score = 100.0
            if lat and lng and p.salon:
                dist = AIStylistMatcherService._haversine(lat, lng, p.salon.latitude, p.salon.longitude)
                distance_score = max(0, 100 - (dist / 0.1))  # 0km=100, 10km=0
            breakdown["distance"] = distance_score
            score += distance_score * WEIGHTS["distance"]

            # 6. Customer preference (10%) – NEW
            preference_score = 50.0  # neutral default
            if customer:
                if customer.preferred_stylist_id == p.id:
                    preference_score = 100.0   # highest boost
                    breakdown["customer_preference"] = "preferred_stylist"
                elif p.id in past_stylist_ids:
                    preference_score = 80.0    # previous booking
                    breakdown["customer_preference"] = "past_booking"
                else:
                    preference_score = 50.0
                    breakdown["customer_preference"] = "neutral"
            else:
                breakdown["customer_preference"] = "no_customer_data"

            score += preference_score * WEIGHTS["customer_preference"]
            breakdown["preference_score"] = preference_score

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
                "photo_url": p.photo_url,                    # new
                "specialty": p.specialty,                    # new
                "experience_years": p.experience_years,      # new
                "bio": p.bio,                                # new
                "service_prices": p.service_prices,          # new
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
        if breakdown.get("expertise_match", 0) > 80:
            parts.append("perfect match for your service")
        if breakdown.get("rating", 0) > 90:
            parts.append("highly rated by customers")
        if breakdown.get("review_sentiment", 0) > 70:   # changed from 'sentiment'
            parts.append("excellent reviews")
        return f"{', '.join(parts)}." if parts else "Good overall match."
