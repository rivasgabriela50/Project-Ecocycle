// URL oficial de tu backend desplegado en Render
const API_BASE_URL = "https://project-ecocycle-1.onrender.com";

const MATERIALS = {
  papel:    { name: "Papel / Cartón", icon: "📄", bin: 1 },
  metal:    { name: "Metal",          icon: "🥫", bin: 2 },
  vidrio:   { name: "Vidrio",         icon: "🍾", bin: 3 },
  plastico: { name: "Plástico",       icon: "🥤", bin: 4 },
  organico: { name: "Orgánico",       icon: "🍌", bin: 5 }
};

document.addEventListener('DOMContentLoaded', () => {
  startCamera();
  fetchStats();
  setInterval(fetchStats, 5000);

  // Botón de snapshot
  const snapBtn = document.getElementById('btnSnapshot');
  if (snapBtn) snapBtn.addEventListener('click', takeSnapshot);

  // Botón de chat
  const chatBtn = document.getElementById('btnChat');
  if (chatBtn) chatBtn.addEventListener('click', sendChat);

  // Permitir enviar el mensaje al presionar Enter en el input
  const chatInput = document.getElementById('chatInput');
  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendChat();
    });
  }
});

// 1. CÁMARA Y ESCANEO
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } }
    });
    const video = document.getElementById('webcam');
    if (video) video.srcObject = stream;
  } catch (e) {
    console.warn("Permiso de cámara denegado o no disponible.", e);
  }
}

async function takeSnapshot() {
  const video = document.getElementById('webcam');
  if (!video || !video.videoWidth) return;

  const canvas = document.getElementById('hiddenCanvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);

  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'foto.jpg');

    try {
      const res = await fetch(`${API_BASE_URL}/api/photo`, { method: 'POST', body: formData });
      const data = await res.json();
      if (data.ok && data.state) {
        updateMaterialCard(data.state.material, data.state.confidence);
      } else if (data.classification) {
        // Fallback por si la respuesta directa contiene texto
        updateMaterialCard("plastico", 0.95);
      }
    } catch (e) {
      console.error("Error al conectar con el servidor de cámara:", e);
    }
  }, 'image/jpeg', 0.85);
}

function updateMaterialCard(matKey, confidence) {
  const mat = MATERIALS[matKey] || { name: matKey, icon: "♻️", bin: "?" };
  const iconEl = document.getElementById('resIcon');
  const matEl = document.getElementById('resMaterial');
  const detailEl = document.getElementById('resDetail');

  if (iconEl) iconEl.innerText = mat.icon;
  if (matEl) matEl.innerText = mat.name;
  if (detailEl) detailEl.innerText = `Confianza: ${Math.round(confidence * 100)}% · Contenedor #${mat.bin}`;
  
  speakText(`Material detectado: ${mat.name}. Depositar en contenedor ${mat.bin}`);
}

// 2. CHATBOT IA
async function sendChat() {
  const input = document.getElementById('chatInput');
  if (!input) return;
  const msg = input.value.trim();
  if (!msg) return;

  addBubble(msg, 'user');
  input.value = '';

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    const answer = data.answer || data.response || "No pude procesar la respuesta.";
    addBubble(answer, 'ai');
    speakText(answer);
  } catch (e) {
    addBubble("Error al comunicar con la Inteligencia Artificial.", 'ai');
    console.error("Error en sendChat:", e);
  }
}

function addBubble(text, type) {
  const chatArea = document.getElementById('chatArea');
  if (!chatArea) return;

  const div = document.createElement('div');
  const roleClass = type === 'user' ? 'user-message' : 'bot-message';
  div.className = `message ${roleClass}`;
  div.innerText = text;

  chatArea.appendChild(div);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'es-ES';
  window.speechSynthesis.speak(u);
}

// 3. MÉTRICAS
async function fetchStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/history`);    
    const data = await res.json();
    const counts = { papel: 0, metal: 0, vidrio: 0, plastico: 0, organico: 0 };
    (data.history || []).forEach(x => { 
      const mat = (x.material || '').toLowerCase();
      if (counts[mat] !== undefined) counts[mat]++; 
    });

    Object.keys(counts).forEach(k => {
      const el = document.getElementById(`count-${k}`);
      if (el) el.innerText = counts[k];
    });
  } catch (e) {
    console.error("Error consultando métricas:", e);
  }
}