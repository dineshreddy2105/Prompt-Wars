import google.generativeai as genai

API_KEY = "AIzaSyCg2yq6NH_gNTuiRWQON_6FmjQbrldJYdY"
genai.configure(api_key=API_KEY)

print("Supported models for this key:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print("-", m.name)
except Exception as e:
    print(f"Failed to list models: {e}")
