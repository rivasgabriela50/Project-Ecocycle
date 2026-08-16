import os
import time
import base64
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIGURACIÓN
# =========================================================
raw_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
API_KEY = raw_key.strip() if raw_key else None

if API_KEY:
    print(f"✅ API_KEY detectada correctamente (Longitud: {len(API_KEY)})")
else:
    print("❌ ADVERTENCIA: La variable de entorno GEMINI_API_KEY no está configurada en Render.")

def call_gemini_rest(prompt, image_bytes=None, mime_type="image/jpeg", system_instruction=None):
    if not API_KEY:
        return "Error: La API Key no está configurada en las variables de entorno de Render.", "ninguno"

    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}

    parts = []
    if system_instruction:
        parts.append({"text": f"[{system_instruction}]\n\n"})
    parts.append({"text": prompt})

    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded_image
            }
        })

    payload = {
        "contents": [{
            "parts": parts
        }]
    }

    # Intentamos directamente con los dos endpoints y versiones más estables de Google AI
    endpoints_to_try = [
        ("https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent", "gemini-1.5-flash (v1)"),
        ("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", "gemini-1.5-flash (v1beta)"),
        ("https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent", "gemini-pro (v1)")
    ]

    last_error = ""

    for api_url, model_name in endpoints_to_try:
        try:
            response = requests.post(api_url, headers=headers, params=params, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                candidate = data.get("candidates", [])[0]
                text_response = candidate.get("content", {}).get("parts", [])[0].get("text", "")
                return text_response, model_name
            else:
                last_error = response.text
                continue
        except Exception as e:
            last_error = str(e)
            continue

    return f"Error técnico: Ningún modelo respondió. Detalle: {last_error}", "error"

# =========================================================
# RUTAS
# =========================================================
@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "project": "Project-Ecocycle / ECOStation V2",
        "api_key_configured": bool(API_KEY),
        "endpoints": [
            "/api/photo",
            "/api/chat",
            "/api/history"
        ]
    })

@app.route("/api/photo", methods=["POST"])
def classify_photo():
    time.sleep(1)
    
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No se proporcionó ninguna imagen."}), 400
    
    image_file = request.files["image"]
    image_bytes = image_file.read()
    
    if not image_bytes:
        return jsonify({"success": False, "error": "La imagen está vacía."}), 400

    mime_type = image_file.content_type or "image/jpeg"

    prompt = """
Analiza cuidadosamente la imagen. Identifica el objeto o residuo que aparece y clasifícalo estrictamente en UNA de estas categorías principales:
- PLASTICO
- METAL
- VIDRIO
- PAPEL
- ORGANICO

Comienza tu respuesta indicando claramente la categoría en mayúsculas (ej: PLASTICO, METAL, VIDRIO, PAPEL, ORGANICO), y luego explica brevemente por qué pertenece a esa categoría y cómo debe reciclarse.
"""

    result_text, model_used = call_gemini_rest(prompt, image_bytes=image_bytes, mime_type=mime_type)

    text_lower = result_text.lower()
    detected_material = next((m for m in ["plastico", "metal", "vidrio", "papel", "organico"] if m in text_lower), "otro")

    return jsonify({
        "success": True,
        "model": model_used,
        "state": {
            "material": detected_material,
            "confidence": 0.95,
            "details": result_text
        },
        "classification": result_text
    })

@app.route("/api/chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"success": False, "error": "No se envió mensaje."}), 400

    user_message = data["message"]
    system_inst = "Eres EcoBot, asistente virtual de Project-Ecocycle. Experto en reciclaje, separación de residuos (plástico, metal, vidrio, papel, orgánicos) y sostenibilidad. Responde de forma clara, sencilla y útil a preguntas sobre clasificación de materiales y consejos ambientales."

    result_text, model_used = call_gemini_rest(prompt=user_message, system_instruction=system_inst)

    return jsonify({
        "success": True,
        "model": model_used,
        "answer": result_text,
        "response": result_text
    })

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify({
        "success": True,
        "history": []
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)