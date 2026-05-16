import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env file
load_dotenv()

# Create a client using the GOOGLE_API_KEY environment variable
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Make a simple request to verify connectivity
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one sentence."
)

print("API connection successful!")
print(f"Response: {response.text}")