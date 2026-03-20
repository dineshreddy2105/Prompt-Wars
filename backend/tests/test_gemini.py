from unittest.mock import MagicMock, patch
import pytest
from gemini_bridge import analyze_civic_complaint

def test_analyze_civic_complaint_mocked(mock_gemini_response):
    """Verify the bridge logic handles Gemini responses correctly."""
    
    # Mock the GenerativeModel
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_model_instance = MockModel.return_value
        
        # Mock the response object
        mock_resp = MagicMock()
        mock_resp.text = '{"ticket_metadata": {"issue_category": "Water Leak", "priority_score": 4, "target_department": "Water & Power Authority", "estimated_repair_complexity": "Medium"}, "official_report": {"subject_line": "Major Water Main Leak Report", "description_formalized": "Significant water leakage reported on Main St.", "visual_evidence_summary": "Active flooding observed.", "safety_hazard_warning": "Slippery road."}, "citizen_feedback": {"status_message": "Report received.", "next_steps": "Stay clear."}, "verification_status": "Verified", "confidence_level": "High"}'
        mock_model_instance.generate_content.return_value = mock_resp
        
        # Run the function
        result = analyze_civic_complaint(
            description="Massive water leak on Main St.",
            location="Main St"
        )
        
        # Verify the structure
        assert result["ticket_metadata"]["issue_category"] == "Water Leak"
        assert result["verification_status"] == "Verified"
        assert "ticket_id" in result
        assert MockModel.called

def test_analyze_civic_complaint_with_image_mocked():
    """Verify the bridge logic handles images correctly."""
    
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_model_instance = MockModel.return_value
        mock_resp = MagicMock()
        mock_resp.text = '{"ticket_metadata": {"issue_category": "Pothole", "priority_score": 3, "target_department": "DOT", "estimated_repair_complexity": "Low"}, "official_report": {"subject_line": "Pothole", "description_formalized": "...", "visual_evidence_summary": "...", "safety_hazard_warning": "..."}, "citizen_feedback": {"status_message": "...", "next_steps": "..."}, "verification_status": "Verified", "confidence_level": "High"}'
        mock_model_instance.generate_content.return_value = mock_resp
        
        # Sample dummy image bytes
        dummy_image = b"fakeimagebase64data"
        
        result = analyze_civic_complaint(
            description="Pothole here",
            image_bytes=dummy_image,
            image_mime_type="image/png"
        )
        
        assert result["ticket_metadata"]["issue_category"] == "Pothole"
        assert MockModel.called
        # Verify generate_content was called with a list containing the prompt and image parts
        args, _ = mock_model_instance.generate_content.call_args
        assert len(args[0]) == 2 # Prompt + Image
