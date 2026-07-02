import base64
import os

import requests
from dotenv import load_dotenv

load_dotenv()
# ******* USE LOCAL HOST FOR RUNNING FRUIT BOT ON THE SAME MACHINE AS OLLAMA. USE IP+PORT FOR REMOTE HOSTS. *******
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

FILL_LEVELS = ("full", "partial", "empty")

PROMPT = (
    "You are looking at a photo of a fruit bin. Classify how full the bin "
    "is using exactly one of these three words: full, partial, empty. "
    "It is imperative to respond with only that single word, "
    "no acknowldgement of understanding."
)


def analyze_image(image_path):
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else {}
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": PROMPT,
            "images": [image_b64],
            "stream": False,
        },
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    raw_response = response.json()["response"]

    return {
        "filename": os.path.basename(image_path),
        "fill_level": parse_fill_level(raw_response),
        "raw_response": raw_response,
        "model": OLLAMA_MODEL,
    }


def parse_fill_level(text):
    normalized = text.strip().lower()

    if normalized in FILL_LEVELS:
        return normalized

    if "empty" in normalized:
        return "empty"
    if "partial" in normalized or "half" in normalized:
        return "partial"
    if "full" in normalized:
        return "full"

    raise ValueError(f"Could not parse fill level from response: {text!r}")
