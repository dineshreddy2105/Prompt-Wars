import sys
import google.generativeai as genai

API_KEY = "AIzaSyCg2yq6NH_gNTuiRWQON_6FmjQbrldJYdY"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content("hello")
    print(f"SUCCESS: The API key is valid! Model responded: {resp.text}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: The API key failed the test. Exception: {str(e)}")
    sys.exit(1)
