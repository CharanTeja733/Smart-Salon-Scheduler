from celery import shared_task

from app.services.payment import PaymentService


@shared_task
def process_refund_task(payment_intent_id: str, amount: float):
    """Process refund asynchronously."""
    success = PaymentService.process_refund(payment_intent_id, amount)
    if success:
        return {"status": "refunded", "payment_intent_id": payment_intent_id}
    else:
        return {"status": "failed", "payment_intent_id": payment_intent_id}
