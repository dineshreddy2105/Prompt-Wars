"""
gemini_bridge.py
Core Gemini 1.5 Flash integration for CivicBridge AI.
Handles multimodal input (text + image) and strict JSON output parsing.
"""

import os
import json
import re
import base64
import uuid
from datetime import datetime
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

def get_secret(secret_id: str, project_id: Optional[str] = None) -> Optional[str]:
    """Retrieves a secret from Google Cloud Secret Manager if available."""
    if not project_id:
        return os.getenv(secret_id)
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        return os.getenv(secret_id)

# ──────────────────────────────────────────────
# Gemini Configuration
# ──────────────────────────────────────────────
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
API_KEY = get_secret("GEMINI_API_KEY", PROJECT_ID)

if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not found in environment or Secret Manager.")

genai.configure(api_key=API_KEY)

# ──────────────────────────────────────────────
# System Instruction (The CivicBridge Brain)
# ──────────────────────────────────────────────
SYSTEM_INSTRUCTION = """
You are "CivicBridge AI," an expert Urban Management and Public Works Dispatcher. 
Your mission is to act as a seamless bridge between a frustrated citizen (Human Intent) 
and a rigid Government Administration System (Complex System).

OBJECTIVE:
Take unstructured, "messy" inputs (panicked voice notes, shaky photos of urban issues, 
or slang-filled text) and convert them into a "Verified Official Civic Complaint" in 
STRICT JSON format.

INPUT ANALYSIS STEPS:
1. Visual Verification: Analyze the image to identify the exact issue (e.g., Pothole, 
   Illegal Dumping, Water Leak, Broken Streetlight). Cross-reference the user's words 
   with the visual evidence.
2. Severity Scoring: Assign a priority level (1-5) based on public safety:
   - Level 5: Immediate danger (Live wires, massive water main burst, gas leak, fire)
   - Level 4: Serious hazard (Large pothole on busy road, major flooding)
   - Level 3: Moderate issue (Broken streetlight, minor water leak, fallen tree branch)
   - Level 2: Maintenance needed (Faded road markings, damaged sidewalk)
   - Level 1: Aesthetic/Non-urgent (Graffiti, overgrown grass)
3. Department Mapping: Route to the correct department:
   - Road/Pothole → Department of Transportation
   - Water/Sewage → Water & Power Authority
   - Streetlights/Electrical → Electrical & Power Department
   - Waste/Garbage → Waste Management Division
   - Trees/Parks → Parks & Recreation Department
   - Graffiti → Public Works — Beautification Unit
   - Gas leaks → Emergency Services + Utilities
4. Context Extraction: Extract landmarks, street names, or location clues from the 
   photo or description to help dispatchers locate the issue.

OUTPUT FORMAT — YOU MUST OUTPUT ONLY VALID JSON, NO EXTRA TEXT:
{
  "ticket_metadata": {
    "issue_category": "string (e.g., Pothole, Water Leak, Broken Streetlight)",
    "priority_score": <integer 1-5>,
    "target_department": "string",
    "estimated_repair_complexity": "Low|Medium|High"
  },
  "official_report": {
    "subject_line": "Professional formal title for the ticket",
    "description_formalized": "A professional 3-sentence summary of the complaint",
    "visual_evidence_summary": "Description of what was verified in the photo, or 'No image provided' if absent",
    "safety_hazard_warning": "Specific warning for field workers, or 'No immediate hazard identified'"
  },
  "citizen_feedback": {
    "status_message": "A friendly, encouraging message to the user in their original language",
    "next_steps": "What the user should expect next from the city"
  },
  "verification_status": "Verified|Verification_Failed",
  "confidence_level": "High|Medium|Low"
}

CRITICAL RULES:
- If the user is angry or uses slang, translate it into professional Government-speak.
- If the photo doesn't match the description, set verification_status to "Verification_Failed".
- Be precise: If a pipe is "leaking", use the image to estimate if it's a "slow drip" or "active flooding".
- If input is unclear, do NOT fail. Provide your best guess and set confidence_level to "Low".
- Output MUST be valid JSON only. No markdown, no code fences, no extra explanation.
"""


# ──────────────────────────────────────────────
# Main Bridge Function
# ──────────────────────────────────────────────
def analyze_civic_complaint(
    description: str,
    location: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = "image/jpeg",
) -> dict:
    """
    Sends complaint text + optional image to Gemini 1.5 Flash.
    Returns a parsed dict matching the CivicComplaintResponse schema.
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config=genai.GenerationConfig(
            temperature=0.2,          # Low temp for precise, structured output
            response_mime_type="application/json",
        ),
    )

    # Build the user prompt
    location_context = f"\nLocation hint from user: {location}" if location else ""
    user_prompt = (
        f"Citizen complaint: {description}"
        f"{location_context}\n\n"
        "Analyze this complaint and any attached photo. "
        "Produce the complete JSON civic dispatch ticket."
    )

    # Build content parts
    content_parts = [user_prompt]

    if image_bytes:
        content_parts.append(
            {
                "mime_type": image_mime_type,
                "data": image_bytes,
            }
        )

    # Call Gemini
    response = model.generate_content(content_parts)
    raw_text = response.text.strip()

    # Parse JSON — strip markdown fences if model includes them despite instructions
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    result = json.loads(raw_text)

    # Inject a unique ticket ID and timestamp
    result["ticket_id"] = f"CIV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    return result
