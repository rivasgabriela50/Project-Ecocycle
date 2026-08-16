import os
import time
import base64
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIGURACIÓN (Groq API)
# =========================================================
raw_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
API_KEY = raw_key.strip() if raw_key else None

if API_KEY:
    print(f"✅ API_KEY detectada correctamente (Longitud: {len(API_KEY)})")
else:
    print("❌ ADVERTENCIA: La variable de entorno GROQ_API_KEY no está configurada en Render.")

def call_groq_rest(prompt, image_bytes=None, mime_type="image/jpeg", system_instruction=None):
    if not API_KEY:
        return "Error: La API Key no está configurada en las variables de entorno de Render.", "ninguno"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    
    # Instrucción del sistema si existe
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})

    # Construir el contenido del mensaje del usuario (texto + imagen si la hay)
    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime_type};base64,{encoded_image}"
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            text_response = data.get("choices", [])[0].get("message", {}).get("content", "")
            return text_response, "llama-3.2-11b-vision-preview"
        else:
            return f"Error técnico de Groq ({response.status_code}): {response.text}", "error"
            
    except Exception as e:
        return f"Error técnico: {str(e)}", "error"

# =========================================================
# RUTAS
# =========================================================
@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "project": "Project-Ecocycle / ECOStation V2 (Groq)",
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

Comienza tu respuesta indicando claramente la categoría en mayúsculas (ej: PLASTICO, METAL, VIDRIO, PAPEL, ORGANICO), y luego explica brevemente por qué pertenece a esa categoría y cómo debe reciclarlo.
"""

    result_text, model_used = call_groq_rest(prompt, image_bytes=image_bytes, mime_type=mime_type)

    text_lower = result_text.lower().strip()

    # Detección precisa de materiales
    detected_material = "otro"

    if any(term in text_lower[:50] for term in ["metal", "lata", "aluminio", "acero"]):
        detected_material = "metal"
    elif any(term in text_lower[:50] for term in ["papel", "carton", "cartón", "periodico", "revista"]):
        detected_material = "papel"
    elif any(term in text_lower[:50] for term in ["vidrio", "cristal", "frasco"]):
        detected_material = "vidrio"
    elif any(term in text_lower[:50] for term in ["organico", "orgánico", "restos de comida", "fruta", "vegetal"]):
        detected_material = "organico"
    elif any(term in text_lower[:50] for term in ["plastico", "plástico", "botella de pet", "envase de plastico"]):
        detected_material = "plastico"
    else:
        keywords = {
            "metal": ["metal", "lata", "aluminio", "acero"],
            "papel": ["papel", "carton", "cartón", "periodico", "revista"],
            "vidrio": ["vidrio", "botella de cristal", "frasco"],
            "organico": ["organico", "orgánico", "restos de comida", "fruta", "vegetal"],
            "plastico": ["plastico", "plástico", "botella de pet", "envase de plastico"]
        }
        for material, terms in keywords.items():
            if any(term in text_lower for term in terms):
                detected_material = material
                break

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

    result_text, model_used = call_groq_rest(prompt=user_message, system_instruction=system_inst)

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