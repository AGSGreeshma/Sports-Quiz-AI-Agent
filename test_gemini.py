from google import genai
from src.config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say Hello",
)

print(response.text)