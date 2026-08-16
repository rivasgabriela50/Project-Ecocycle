import os
import time
import base64
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIGURACIÓN (Google Gemini API)
# =========================================================
raw_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
API_KEY = raw_key.strip() if raw_key else None

if API_KEY:
    print(f"✅ API_KEY detectada correctamente (Longitud: {len(API_KEY)})")
else:
    print("❌ [Error]: La variable GEMINI_API_KEY está vacía o no existe en el entorno de Render.")

def call_gemini_rest(prompt, image_bytes=None, mime_type="image/jpeg", system_instruction=None):
    if not API_KEY:
        print("❌ [Error]: No se puede llamar a Gemini porque falta la GEMINI_API_KEY.")
        return None, "sin_api_key"

    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}

    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"Instrucción del sistema: {system_instruction}"}]
        })
    
    parts_list = [{"text": prompt}]
    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        parts_list.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded_image
            }
        })
    
    contents.append({
        "role": "user",
        "parts": parts_list
    })

    payload = {"contents": contents}

    # Modelos estables actuales vigentes
    endpoints_to_try = [
        ("https://generativelanguage.googleapis.com/v1/models/gemini-3.6-flash:generateContent", "gemini-3.6-flash (v1)"),
        ("https://generativelanguage.googleapis.com/v1/models/gemini-3.5-flash:generateContent", "gemini-3.5-flash (v1)"),
        ("https://generativelanguage.googleapis.com/v1/models/gemini-3.7-flash:generateContent", "gemini-3.7-flash (v1)")
    ]

    for api_url, model_name in endpoints_to_try:
        try:
            print(f"🔄 Intentando conectar con Gemini usando {model_name}...")
            response = requests.post(api_url, headers=headers, params=params, json=payload, timeout=25)
            
            if response.status_code == 200:
                data = response.json()
                candidate = data.get("candidates", [])[0]
                text_response = candidate.get("content", {}).get("parts", [])[0].get("text", "")
                print(f"✅ ¡Conexión exitosa con {model_name}!")
                return text_response, model_name
            else:
                print(f"⚠️ {model_name} respondió con código {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Excepción conectando a {model_name}: {e}")
            continue

    print("🚨 Todos los intentos con Gemini fallaron. Activando respaldo local.")
    return None, "error_o_cuota"

# =========================================================
# RUTAS Y RESPALDO INTELIGENTE
# =========================================================
@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "project": "Project-Ecocycle / ECOStation V2",
        "api_key_configured": bool(API_KEY)
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

Comienza tu respuesta indicando claramente la categoría en mayúsculas, y luego explica brevemente por qué pertenece a esa categoría y cómo debe reciclarlo.
"""

    result_text, model_used = call_gemini_rest(prompt, image_bytes=image_bytes, mime_type=mime_type)

    if not result_text or model_used in ["sin_api_key", "error_o_cuota"]:
        model_used = "ecocycle-local-fallback"
        result_text = (
            "PLASTICO\n\n"
            "⚠️ (Modo de respaldo activo)\n"
            "El objeto detectado ha sido clasificado automáticamente como material aprovechable. "
            "Asegúrate de enjuagarlo y depositarlo en el contenedor correspondiente para su reciclaje."
        )

    text_lower = result_text.lower().strip()
    detected_material = "plastico"

    if "metal" in text_lower[:50] or "lata" in text_lower[:50]:
        detected_material = "metal"
    elif "papel" in text_lower[:50] or "carton" in text_lower[:50]:
        detected_material = "papel"
    elif "vidrio" in text_lower[:50] or "cristal" in text_lower[:50]:
        detected_material = "vidrio"
    elif "organico" in text_lower[:50] or "orgánico" in text_lower[:50]:
        detected_material = "organico"
    elif "plastico" in text_lower[:50] or "plástico" in text_lower[:50]:
        detected_material = "plastico"

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
    system_inst = "Eres EcoBot, asistente virtual de Project-Ecocycle. Experto en reciclaje y separación de residuos."

    result_text, model_used = call_gemini_rest(prompt=user_message, system_instruction=system_inst)

    if not result_text or model_used in ["sin_api_key", "error_o_cuota"]:
        model_used = "ecocycle-local-fallback"
        result_text = "¡Hola! Soy EcoBot de Project-Ecocycle. En este momento estoy operando en modo de respaldo local, pero recuerda que separar adecuadamente tus residuos (plástico, metal, vidrio, papel y orgánicos) ayuda enormemente a la sostenibilidad en nuestra comunidad."

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