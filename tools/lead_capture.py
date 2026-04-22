"""
Lead Capture Tool for Social-to-Lead Agentic Workflow
Captures and stores potential customer information
"""

import json
import os
from datetime import datetime
from typing import Optional


class LeadCaptureTool:
    """Tool for capturing and storing lead information."""

    def __init__(self, storage_file: str = "leads.json"):
        self.storage_file = storage_file
        self.leads = self._load_leads()

    def _load_leads(self) -> list:
        """Load existing leads from storage."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_leads(self) -> None:
        """Save leads to storage file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.leads, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save leads: {e}")

    def capture_lead(
        self,
        name: str,
        email: str,
        company: Optional[str] = None,
        phone: Optional[str] = None,
        interest: Optional[str] = None,
        source: str = "chat"
    ) -> dict:
        """
        Capture a new lead.

        Args:
            name: Lead's full name
            email: Lead's email address
            company: Lead's company name (optional)
            phone: Lead's phone number (optional)
            interest: What the lead is interested in (optional)
            source: Source of the lead (default: "chat")

        Returns:
            dict: Captured lead data with confirmation
        """
        lead = {
            "id": len(self.leads) + 1,
            "name": name,
            "email": email,
            "company": company,
            "phone": phone,
            "interest": interest,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "status": "new"
        }

        self.leads.append(lead)
        self._save_leads()

        return {
            "success": True,
            "message": f"Lead captured successfully! We will contact {name} at {email} shortly.",
            "lead_id": lead["id"],
            "lead": lead
        }

    def get_all_leads(self) -> list:
        """Get all captured leads."""
        return self.leads

    def get_lead_by_email(self, email: str) -> Optional[dict]:
        """Find a lead by email address."""
        for lead in self.leads:
            if lead["email"].lower() == email.lower():
                return lead
        return None

    def update_lead_status(self, lead_id: int, status: str) -> dict:
        """
        Update the status of a lead.

        Args:
            lead_id: ID of the lead to update
            status: New status (e.g., "contacted", "qualified", "converted")

        Returns:
            dict: Update result
        """
        for lead in self.leads:
            if lead["id"] == lead_id:
                lead["status"] = status
                lead["updated_at"] = datetime.now().isoformat()
                self._save_leads()
                return {"success": True, "message": f"Lead {lead_id} status updated to {status}"}

        return {"success": False, "message": f"Lead {lead_id} not found"}

    def get_leads_summary(self) -> dict:
        """Get a summary of all leads."""
        total = len(self.leads)
        by_status = {}
        for lead in self.leads:
            status = lead.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_leads": total,
            "by_status": by_status,
            "latest_lead": self.leads[-1] if self.leads else None
        }
