"""
Booking Tool - Schedules demo calls for high-intent leads.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BookingTool:
    """
    Tool for scheduling demo calls with high-intent leads.
    In production, this would integrate with Calendly, Google Calendar, etc.
    """
    
    def schedule_demo(self, name: str, email: str, preferred_time: str = None) -> str:
        """
        Schedule a demo call for a lead.
        
        Args:
            name: Lead name
            email: Lead email
            preferred_time: Optional preferred time slot
            
        Returns:
            Confirmation message string
        """
        # Generate available slots (in production, fetch from calendar API)
        slots = self._get_available_slots()
        
        # Select the first available slot or use preferred time
        selected_slot = slots[0] if slots else self._get_default_slot()
        
        booking_ref = self._generate_booking_ref(name, email)
        
        logger.info(f"Demo booked for {name} ({email}) at {selected_slot}")
        
        return (
            f"**Demo Call Scheduled!**\n"
            f"Date: {selected_slot}\n"
            f"Booking Reference: {booking_ref}\n"
            f"A calendar invite will be sent to {email}.\n"
            f"Call duration: 30 minutes"
        )
    
    def _get_available_slots(self) -> list:
        """Get next 3 available demo slots (Mon-Fri, 10am-4pm)."""
        slots = []
        current = datetime.now()
        
        # Find next 3 business day slots
        days_checked = 0
        while len(slots) < 3 and days_checked < 14:
            current += timedelta(days=1)
            days_checked += 1
            
            # Skip weekends
            if current.weekday() >= 5:
                continue
            
            # Add morning and afternoon slots
            morning = current.replace(hour=10, minute=0, second=0, microsecond=0)
            afternoon = current.replace(hour=14, minute=0, second=0, microsecond=0)
            
            slots.append(morning.strftime("%A, %B %d at 10:00 AM IST"))
            if len(slots) < 3:
                slots.append(afternoon.strftime("%A, %B %d at 2:00 PM IST"))
        
        return slots[:3]
    
    def _get_default_slot(self) -> str:
        """Get a default slot for tomorrow."""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%A, %B %d at 10:00 AM IST")
    
    def _generate_booking_ref(self, name: str, email: str) -> str:
        """Generate a booking reference."""
        import hashlib
        import time
        data = f"{name}{email}{time.time()}"
        return "DEMO-" + hashlib.md5(data.encode()).hexdigest()[:6].upper()
    
    def get_available_slots(self) -> str:
        """Get formatted available slots string."""
        slots = self._get_available_slots()
        lines = ["**Available Demo Slots:**"]
        for i, slot in enumerate(slots, 1):
            lines.append(f"  {i}. {slot}")
        lines.append("\nReply with your preferred slot number or suggest another time.")
        return "\n".join(lines)
