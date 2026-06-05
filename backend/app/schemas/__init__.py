# backend/app/schemas/__init__.py
from .ai import (
    DemandPredictionResponse,
    SentimentResponse,
    StylistMatchRequest,
    StylistMatchResponse,
)
from .appointment import (
    AppointmentStatusResponse,
    BookingRequest,
    BookingResponse,
    CancelRequest,
    CancelResponse,
    ConfirmRequest,
    RescheduleRequest,
)
from .customer import Customer, CustomerResponse, CustomerUpdate
from .practitioner import (
    AvailabilityRequest,
    AvailabilityResponse,
    DeactivateRequest,
    Practitioner,
    PractitionerResponse,
    UnavailableRequest,
)
from .review import ReviewCreate, ReviewResponse
from .salon import Salon, SalonResponse, SalonSearchParams
from .waitlist import WaitlistCreate, WaitlistResponse, WaitlistStatusResponse

__all__ = [
    "Salon", "SalonSearchParams", "SalonResponse",
    "Practitioner", "PractitionerResponse", "AvailabilityRequest", "AvailabilityResponse", "UnavailableRequest", "DeactivateRequest",
    "Customer", "CustomerResponse", "CustomerUpdate",
    "BookingRequest", "BookingResponse", "ConfirmRequest", "CancelRequest", "CancelResponse",
    "RescheduleRequest", "AppointmentStatusResponse",
    "ReviewCreate", "ReviewResponse",
    "WaitlistCreate", "WaitlistResponse", "WaitlistStatusResponse",
    "StylistMatchRequest", "StylistMatchResponse", "SentimentResponse", "DemandPredictionResponse",
]
