from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RepairComplexity(str, Enum):
    """Enumeration of possible repair complexities for public works dispatch."""
    Low = "Low"
    Medium = "Medium"
    High = "High"


class TicketMetadata(BaseModel):
    """Metadata for routing and prioritizing the civic complaint."""
    issue_category: str = Field(..., description="Category of the civic issue")
    priority_score: int = Field(..., ge=1, le=5, description="Priority from 1 (low) to 5 (critical)")
    target_department: str = Field(..., description="Government department to route the complaint to")
    estimated_repair_complexity: RepairComplexity = Field(..., description="Estimated repair complexity")


class OfficialReport(BaseModel):
    """The formalized, structured report generated from the original messy citizen input."""
    subject_line: str = Field(..., description="Professional formal title for the ticket")
    description_formalized: str = Field(..., description="3-sentence professional summary of the complaint")
    visual_evidence_summary: str = Field(..., description="Description of verified visual evidence from photo")
    safety_hazard_warning: str = Field(..., description="Specific safety warning for field workers")


class CitizenFeedback(BaseModel):
    """Translated and friendly status updates intended explicitly for the citizen reporting the issue."""
    status_message: str = Field(..., description="Friendly message to the user in their language")
    next_steps: str = Field(..., description="What the user should expect next from the city")


class CivicComplaintResponse(BaseModel):
    """The ultimate structured response combining metadata, reports, and citizen feedback."""
    ticket_metadata: TicketMetadata
    official_report: OfficialReport
    citizen_feedback: CitizenFeedback
    verification_status: Optional[str] = Field(
        default="Verified",
        description="'Verified' or 'Verification_Failed' if photo doesn't match description"
    )
    confidence_level: Optional[str] = Field(
        default="High",
        description="'High', 'Medium', or 'Low' confidence in the analysis"
    )
    ticket_id: Optional[str] = Field(default=None, description="Generated ticket ID")


class ComplaintRequest(BaseModel):
    """Incoming request schema for JSON tests (though multipart forms are standard)."""
    description: str
    location: Optional[str] = None
