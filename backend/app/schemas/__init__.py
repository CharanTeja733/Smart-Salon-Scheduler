# backend/app/schemas/__init__.py
from .salon import Salon, SalonSearchParams, SalonResponse
from .practitioner import Practitioner, PractitionerResponse, AvailabilityRequest, AvailabilityResponse
from .customer import Customer, CustomerResponse, CustomerUpdate
from .appointment import (
    BookingRequest, BookingResponse,
    ConfirmRequest, CancelRequest, CancelResponse,
    RescheduleRequest, AppointmentStatusResponse
)
from .review import ReviewCreate, ReviewResponse
from .waitlist import WaitlistCreate, WaitlistResponse, WaitlistStatusResponse
from .ai import StylistMatchRequest, StylistMatchResponse, SentimentResponse, DemandPredictionResponse

__all__ = [
    "Salon", "SalonSearchParams", "SalonResponse",
    "Practitioner", "PractitionerResponse", "AvailabilityRequest", "AvailabilityResponse",
    "Customer", "CustomerResponse", "CustomerUpdate",
    "BookingRequest", "BookingResponse", "ConfirmRequest", "CancelRequest", "CancelResponse",
    "RescheduleRequest", "AppointmentStatusResponse",
    "ReviewCreate", "ReviewResponse",
    "WaitlistCreate", "WaitlistResponse", "WaitlistStatusResponse",
    "StylistMatchRequest", "StylistMatchResponse", "SentimentResponse", "DemandPredictionResponse",
]