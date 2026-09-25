import os
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(api_key=HF_TOKEN, provider="auto")

def sanitize_filename(text):
    filename = re.sub(r"[^a-zA-Z0-9_-]","_", text)
    return filename[:100]

def generate_image(prompt, filename=None):
    if not filename:
        filename = sanitize_filename(prompt) + ".png"

    image = client.text_to_image(prompt=prompt, model="black-forest-labs/FLUX.1-schnell")
    path = f"static/panels/{filename}"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    image.save(path)

    return path