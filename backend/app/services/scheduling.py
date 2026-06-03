# backend/app/services/scheduling_service.py
from datetime import datetime, timedelta, date, time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories import PractitionerRepository, AppointmentRepository
from app.models.practitioner import Practitioner

class SchedulingService:
    SLOT_DURATION_MINUTES = 30

    @staticmethod
    def generate_available_slots(
        practitioner_id: int,
        target_date: date,
        db: Session,
        service_duration: int = 30
    ) -> List[datetime]:
        """
        Generate all available time slots for a practitioner on a specific date.
        Handles:
        - Opening hours (salon default or practitioner override)
        - Lunch breaks
        - Off days (recurring or specific dates)
        - Existing appointments (including longer services that block multiple slots)
        """
        practitioner_repo = PractitionerRepository()
        appointment_repo = AppointmentRepository()

        practitioner = practitioner_repo.get_by_id(db, practitioner_id)
        if not practitioner or not practitioner.is_active:
            return []

        # 1. Check if practitioner is off on this date
        if SchedulingService._is_off_day(practitioner, target_date):
            return []

        # 2. Get operating hours
        open_time, close_time = SchedulingService._get_operating_hours(practitioner, target_date)
        if not open_time or not close_time:
            return []

        # 3. Generate candidate slots at SLOT_DURATION_MINUTES intervals
        start_dt = datetime.combine(target_date, open_time)
        end_dt = datetime.combine(target_date, close_time)
        candidate_slots = []
        current = start_dt
        while current + timedelta(minutes=SchedulingService.SLOT_DURATION_MINUTES) <= end_dt:
            candidate_slots.append(current)
            current += timedelta(minutes=SchedulingService.SLOT_DURATION_MINUTES)

        # 4. Filter out slots that conflict with lunch breaks
        candidate_slots = SchedulingService._filter_lunch_break(practitioner, candidate_slots)

        # 5. Filter out slots that are already booked (or needed for longer appointments)
        available = []
        for slot in candidate_slots:
            slot_end = slot + timedelta(minutes=service_duration)
            # Check overlapping appointments
            overlapping = appointment_repo.get_overlapping(
                db, practitioner_id, slot, slot_end, for_update=False
            )
            if not overlapping:
                available.append(slot)

        return available

    @staticmethod
    def _is_off_day(practitioner: Practitioner, target_date: date) -> bool:
        weekday = target_date.strftime("%A").lower()
        off_days = practitioner.off_days or []
        # Check recurring weekday
        if weekday in off_days:
            return True
        # Check specific date string (YYYY-MM-DD)
        date_str = target_date.isoformat()
        if date_str in off_days:
            return True
        return False

    @staticmethod
    def _get_operating_hours(practitioner: Practitioner, target_date: date):
        weekday = target_date.strftime("%A").lower()
        # Try practitioner override
        if practitioner.default_opening_hours and weekday in practitioner.default_opening_hours:
            hours = practitioner.default_opening_hours[weekday]
            if hours and hours != "closed":
                open_str, close_str = hours.split("-")
                return time.fromisoformat(open_str), time.fromisoformat(close_str)
        # Fallback to salon hours
        salon = practitioner.salon
        if salon.opening_hours and weekday in salon.opening_hours:
            hours = salon.opening_hours[weekday]
            if hours and hours != "closed":
                open_str, close_str = hours.split("-")
                return time.fromisoformat(open_str), time.fromisoformat(close_str)
        return None, None

    @staticmethod
    def _filter_lunch_break(practitioner: Practitioner, slots: List[datetime]) -> List[datetime]:
        if not practitioner.lunch_break_start or not practitioner.lunch_break_end:
            return slots
        filtered = []
        for slot in slots:
            slot_time = slot.time()
            if not (practitioner.lunch_break_start <= slot_time < practitioner.lunch_break_end):
                filtered.append(slot)
        return filtered