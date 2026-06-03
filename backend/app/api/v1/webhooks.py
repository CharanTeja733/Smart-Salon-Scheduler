from fastapi import APIRouter, Request, HTTPException
import stripe
from app.config import settings
from app.services.payment_service import PaymentService
from app.services.booking_service import BookingService
from sqlalchemy.orm import Session
from app.database import SessionLocal

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        appointment_id = payment_intent["metadata"].get("appointment_id")
        if appointment_id:
            db = SessionLocal()
            await BookingService.confirm_booking(int(appointment_id), payment_intent["id"], db)
            db.close()
    
    return {"status": "received"}