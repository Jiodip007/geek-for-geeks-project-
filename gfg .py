import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if not client:
        return jsonify({"error": "Gemini API key is not configured in .env file."}), 500

    data = request.json
    error_message = data.get("error_message", "").strip()
    language = data.get("language", "JavaScript")

    if not error_message:
        return jsonify({"error": "Please enter an error message."}), 400

    prompt = f"""
    You are DEVFIX, an expert code analyzer.
    Analyze the following error in {language}:
    
    "{error_message}"

    Respond strictly in JSON format matching this exact schema:
    {{
        "what_happened": "A clear 1-2 sentence high level explanation of what went wrong.",
        "why_happened": "2-3 key reasons why this error typically occurs.",
        "possible_cause": "A direct explanation of the root cause for this specific snippet.",
        "suggested_fix": "Detailed step-by-step resolution including corrected code examples."
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)