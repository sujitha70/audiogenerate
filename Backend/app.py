import base64
import os
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Automatically load environment variables from .env file (check Backend/ and root)
try:
    from dotenv import load_dotenv
    load_dotenv()
    backend_env = Path(__file__).parent / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
except ImportError:
    pass

try:
    from google import genai
except ImportError:  # pragma: no cover - optional dependency for local tests
    genai = None

# Configure Flask app to serve Frontend static assets
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

MURF_API_KEY = os.getenv("MURF_API_KEY", "YOUR_MURF_API_KEY_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if genai and GEMINI_API_KEY else None

PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",
    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
""",
}


def generate_speech(text, voice_id, locale):
    if not MURF_API_KEY or MURF_API_KEY == "YOUR_MURF_API_KEY_HERE":
        raise RuntimeError("MURF_API_KEY environment variable is missing or not configured.")

    url = "https://global.api.murf.ai/v1/speech/stream"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "voice_id": voice_id,
        "text": text,
        "locale": locale,
        "model": "FALCON",
        "format": "MP3",
        "sampleRate": 24000,
        "channelType": "MONO",
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)

    if response.status_code == 200:
        return response.content

    raise RuntimeError(f"Murf API error: {response.status_code} - {response.text[:200]}")


def generate_description(place, answer_type, language):
    if client is None:
        raise RuntimeError("GEMINI_API_KEY environment variable is missing or invalid.")

    if answer_type not in PROMPTS:
        raise ValueError(f"Unsupported answer type: {answer_type}")

    prompt = PROMPTS[answer_type].format(place=place, language=language)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
    )
    return getattr(response, "text", str(response))


# Route for root: serve Frontend index.html
@app.route("/", methods=["GET"])
def serve_index():
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return jsonify({"status": "healthy", "service": "Travel Guide API"})


# Health check endpoint for cloud monitoring / ping
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Travel Guide API"})


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.get_json(silent=True) or {}

    missing_fields = [
        field for field in ("place", "answerType", "language", "voiceId", "locale") if field not in data
    ]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    place = data["place"]
    answer_type = data["answerType"]
    language = data["language"]
    voice_id = data["voiceId"]
    locale = data["locale"]

    try:
        text_description = generate_description(place, answer_type, language)
        audio_bytes = generate_speech(text_description, voice_id, locale)
        encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
        return jsonify({
            "description": text_description,
            "audioBase64": encoded_audio,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)