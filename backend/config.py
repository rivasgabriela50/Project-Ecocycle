def call_gemini_rest(prompt, image_bytes=None, mime_type="image/jpeg", system_instruction=None):
    if not API_KEY:
        print("❌ [Error]: La variable GEMINI_API_KEY está vacía o no existe en el entorno.")
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

    # Modelos oficiales estables actuales
    endpoints_to_try = [
        ("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", "gemini-2.0-flash"),
        ("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", "gemini-1.5-flash")
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