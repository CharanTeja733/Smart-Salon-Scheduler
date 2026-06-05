from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.customer import Customer

from .base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)

    def get_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        return db.query(self.model).filter(self.model.phone == phone).first()

    def get_or_create(self, db: Session, phone: str, name: str, email: Optional[str] = None) -> Customer:
        customer = self.get_by_phone(db, phone)
        if not customer:
            customer = self.create(db, phone=phone, name=name, email=email)
        else:
            if customer.name != name:
                customer.name = name
            if email and customer.email != email:
                customer.email = email
            db.flush()
        return customer

    def increment_appointment_count(self, db: Session, customer_id: int, amount_spent: float = 0):
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.total_appointments += 1
            customer.total_spent += amount_spent
            customer.last_booking_at = func.now()
            db.flush()

    def increment_no_show(self, db: Session, customer_id: int):
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.no_show_count += 1
            db.flush()
