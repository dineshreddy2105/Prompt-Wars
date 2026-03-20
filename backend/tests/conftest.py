import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_complaint():
    """Standard complaint data for tests."""
    return {
        "description": "The water pipe on Main St is leaking significantly.",
        "location": "Main St & 5th Ave"
    }

@pytest.fixture
def mock_gemini_response():
    """Mock JSON response from Gemini."""
    return {
        "ticket_metadata": {
            "issue_category": "Water Leak",
            "priority_score": 4,
            "target_department": "Water & Power Authority",
            "estimated_repair_complexity": "Medium"
        },
        "official_report": {
            "subject_line": "Major Water Main Leak Report",
            "description_formalized": "Significant water leakage reported on Main St. Immediate attention required.",
            "visual_evidence_summary": "Active flooding observed in street photo.",
            "safety_hazard_warning": "Slippery road conditions and potential sinkhole."
        },
        "citizen_feedback": {
            "status_message": "We have received your report and a crew is being dispatched.",
            "next_steps": "Please stay clear of the flooding area."
        },
        "verification_status": "Verified",
        "confidence_level": "High",
        "ticket_id": "CIV-2026-TEST-123"
    }
