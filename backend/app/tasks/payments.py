from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.payment_service import PaymentService

@shared_task
def process_refund_task(payment_intent_id: str, amount: float):
    """Process refund asynchronously."""
    success = await PaymentService.process_refund(payment_intent_id, amount)
    if success:
        return {"status": "refunded", "payment_intent_id": payment_intent_id}
    else:
        return {"status": "failed", "payment_intent_id": payment_intent_id}