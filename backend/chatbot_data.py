"""
Datos y estructuras para el sistema de chatbot educativo de Ecocycle
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class ConversationTopic(Enum):
    """Tópicos de conversación disponibles"""
    PRODUCTO = "producto"
    SOSTENIBILIDAD = "sostenibilidad"
    TECNOLOGIA = "tecnologia"
    CONTACTO = "contacto"
    EDUCACION = "educacion"
    MANTENIMIENTO = "mantenimiento"
    PREGUNTAS_FRECUENTES = "preguntas_frecuentes"


@dataclass
class ChatbotResponse:
    """Estructura de respuesta del chatbot"""
    mensaje: str
    confianza: float
    topico: ConversationTopic
    requiere_humano: bool = False
    sugerencias_seguimiento: List[str] = field(default_factory=list)


# Base de conocimientos sobre Ecocycle
KNOWLEDGE_BASE = {
    ConversationTopic.PRODUCTO: {
        "descripcion": "Ecocycle es un prototipo industrial sostenible que optimiza procesos utilizando energía renovable",
        "caracteristicas": [
            "Eficiencia energética superior al 85%",
            "Componentes 100% reciclables",
            "Operación modular y escalable",
            "Bajo consumo de recursos naturales",
            "Vida útil extendida (60+ meses)"
        ],
        "ventajas": [
            "Reduce emisiones de CO2 hasta 50%",
            "Ahorro energético de 30-40% vs sistemas convencionales",
            "Costo operacional reducido",
            "Fácil mantenimiento",
            "Compatible con redes inteligentes"
        ],
        "aplicaciones": [
            "Industria manufacturera",
            "Generación de energía limpia",
            "Sistemas de desalinización",
            "Agricultura sostenible",
            "Gestión de residuos"
        ]
    },
    
    ConversationTopic.SOSTENIBILIDAD: {
        "impacto_ambiental": {
            "reduccion_emisiones": "Cada unidad de Ecocycle reduce 2.5 toneladas de CO2 anuales",
            "ahorro_agua": "Ahorra 10,000+ litros de agua por año en procesos optimizados",
            "uso_tierra": "Reduce huella territorial un 40% vs métodos convencionales",
            "biodiversidad": "Protege ecosistemas locales mediante procesos no contaminantes"
        },
        "objetivos_sostenibilidad": [
            "Alineado con ODS 7 (Energía limpia y asequible)",
            "Alineado con ODS 9 (Industria, innovación e infraestructura)",
            "Alineado con ODS 12 (Consumo y producción responsables)",
            "Alineado con ODS 13 (Acción por el clima)"
        ],
        "certificaciones": [
            "ISO 14001 (Gestión ambiental)",
            "Carbon Trust Standard",
            "Cradle to Cradle certification"
        ]
    },
    
    ConversationTopic.TECNOLOGIA: {
        "componentes_principales": {
            "motor_hibrido": "Sistema de doble fuente: energía solar + energía cinética recuperada",
            "controlador_inteligente": "IA que optimiza operación en tiempo real",
            "bateria_hibrida": "Almacenamiento de energía con supercapacitores",
            "sistema_amortiguamiento": "Recupera energía de vibraciones y movimientos"
        },
        "especificaciones": {
            "potencia_entrada": "2000W (max)",
            "potencia_salida": "1700W (eficiencia 85%)",
            "temperatura_operacion": "15-45°C",
            "rendimiento_maximo": "89% bajo condiciones óptimas",
            "voltaje": "380-480V (3 fases)"
        },
        "integraciones": [
            "Compatible con IoT y sistemas SCADA",
            "API REST para monitoreo remoto",
            "Integración con paneles solares",
            "Conectividad 4G/5G/LoRaWAN"
        ]
    },
    
    ConversationTopic.CONTACTO: {
        "informacion": {
            "email": "info@ecocycle.com",
            "telefono": "+1-800-ECOCYCLE",
            "website": "www.ecocycle.com",
            "ubicacion": "Santa Ana, El Salvador"
        },
        "departamentos": {
            "ventas": "sales@ecocycle.com",
            "soporte_tecnico": "support@ecocycle.com",
            "demostraciones": "demo@ecocycle.com",
            "asociaciones": "partnerships@ecocycle.com"
        },
        "horario_atencion": "Lunes a Viernes: 8:00 AM - 6:00 PM CST"
    },
    
    ConversationTopic.EDUCACION: {
        "contenido_educativo": [
            "Guías de instalación paso a paso",
            "Tutoriales en video sobre optimización",
            "Webinars mensuales sobre sostenibilidad",
            "Certificaciones de operación Ecocycle",
            "Recursos académicos y de investigación"
        ],
        "programas_capacitacion": {
            "nivel_basico": "Introducción a energías renovables (8 horas)",
            "nivel_intermedio": "Operación y mantenimiento de Ecocycle (20 horas)",
            "nivel_avanzado": "Optimización y troubleshooting (40 horas)",
            "nivel_experto": "Diseño e implementación (60 horas)"
        },
        "certificaciones_disponibles": [
            "Certified Ecocycle Operator",
            "Certified Ecocycle Technician",
            "Certified Ecocycle Engineer"
        ]
    },
    
    ConversationTopic.MANTENIMIENTO: {
        "mantenimiento_preventivo": {
            "mensual": [
                "Inspeccionar conexiones eléctricas",
                "Limpiar filtros de entrada de aire",
                "Verificar niveles de refrigerante"
            ],
            "trimestral": [
                "Prueba de rendimiento completa",
                "Calibración de sensores",
                "Limpieza profunda de componentes"
            ],
            "anual": [
                "Reemplazo de piezas de desgaste",
                "Certificación de seguridad",
                "Actualización de firmware"
            ]
        },
        "duracion_componentes": {
            "motor": "60 meses",
            "baterias": "36-48 meses",
            "filtros": "12 meses",
            "fluidos": "12-24 meses"
        },
        "diagnostico": {
            "baja_eficiencia": "Verificar limpieza de sensores y calibración",
            "sobrecalentamiento": "Revisar sistemas de disipación térmica",
            "perdida_potencia": "Chequear baterías y conexiones",
            "errores_sistema": "Actualizar firmware a última versión"
        }
    },
    
    ConversationTopic.PREGUNTAS_FRECUENTES: {
        "faq": [
            {
                "pregunta": "¿Cuál es la vida útil de Ecocycle?",
                "respuesta": "Con mantenimiento adecuado, 60+ meses de operación. Componentes individuales pueden reemplazarse."
            },
            {
                "pregunta": "¿Es compatible con infraestructura existente?",
                "respuesta": "Sí, Ecocycle se integra fácilmente con sistemas existentes gracias a sus interfaces estándar."
            },
            {
                "pregunta": "¿Cuál es el ROI esperado?",
                "respuesta": "Típicamente 3-4 años, con ahorros energéticos anuales del 30-40%."
            },
            {
                "pregunta": "¿Requiere capacitación especial?",
                "respuesta": "Ofrecemos programas de capacitación gratuitos. Operación básica requiere ~2 horas."
            },
            {
                "pregunta": "¿Qué sucede si hay falla?",
                "respuesta": "Sistema de redundancia automática. Soporte técnico 24/7 disponible."
            },
            {
                "pregunta": "¿Cuál es el costo de mantenimiento?",
                "respuesta": "Aproximadamente 5-8% del costo operacional anual vs 15-20% de sistemas convencionales."
            },
            {
                "pregunta": "¿Es escalable?",
                "respuesta": "Sí, arquitectura modular permite escalado desde 1kW a 1MW+"
            },
            {
                "pregunta": "¿Tiene garantía?",
                "respuesta": "Garantía de 36 meses + opciones de extensión disponibles."
            }
        ]
    }
}


# Patrones de entrada comunes del usuario
INTENT_PATTERNS = {
    "producto_info": [
        "¿qué es ecocycle?",
        "cuéntame sobre ecocycle",
        "características de ecocycle",
        "cómo funciona",
        "ventajas del sistema"
    ],
    "precio": [
        "¿cuál es el precio?",
        "costo",
        "presupuesto",
        "cuánto cuesta",
        "tarifa"
    ],
    "disponibilidad": [
        "¿dónde lo venden?",
        "dónde puedo comprar",
        "disponibilidad",
        "stocks",
        "entregas"
    ],
    "soporte": [
        "necesito ayuda",
        "problema técnico",
        "no funciona",
        "error",
        "soporte técnico"
    ],
    "contacto": [
        "contacto",
        "teléfono",
        "email",
        "hablar con alguien",
        "atención al cliente"
    ],
    "sostenibilidad": [
        "impacto ambiental",
        "emisiones",
        "sostenibilidad",
        "energía limpia",
        "verde"
    ],
    "instalacion": [
        "cómo instalar",
        "instalación",
        "setup",
        "configuración",
        "puesta en marcha"
    ],
    "mantenimiento": [
        "mantenimiento",
        "limpieza",
        "reparación",
        "servicio técnico",
        "actualizaciones"
    ]
}


# Respuestas predeterminadas amigables
FRIENDLY_RESPONSES = {
    "bienvenida": "¡Hola! Soy el asistente de Ecocycle. ¿En qué puedo ayudarte hoy? Puedo hablar sobre nuestro producto, sostenibilidad, tecnología, o cualquier otra pregunta que tengas.",
    "despedida": "¡Gracias por usar Ecocycle! Si tienes más preguntas, no dudes en volver. ¡Que tengas un excelente día!",
    "no_entiendo": "Disculpa, no entendí muy bien tu pregunta. ¿Podrías reformularla? Puedo ayudarte con:\n- Información del producto\n- Características técnicas\n- Impacto ambiental\n- Soporte técnico\n- Contacto con nuestro equipo",
    "error": "Parece que hay un problema. Estoy transfiriendo tu consulta a nuestro equipo de soporte. Alguien se comunicará contigo pronto.",
    "gracias": "¡De nada! Estoy aquí para ayudarte. ¿Hay algo más que quieras saber?",
    "opinion": "Valoramos tu opinión. Por favor, comparte tus comentarios en feedback@ecocycle.com o llamando al +1-800-ECOCYCLE."
}


# Contexto del usuario para seguimiento de conversación
@dataclass
class UserContext:
    """Contexto de la sesión del usuario"""
    user_id: str
    idioma: str = "es"
    temas_discutidos: List[ConversationTopic] = field(default_factory=list)
    historial_mensajes: List[Dict] = field(default_factory=list)
    preferencias: Dict = field(default_factory=dict)
    estado_sesion: str = "activa"  # activa, suspendida, escalada
    requiere_seguimiento: bool = False
    
    def agregar_mensaje(self, rol: str, contenido: str, topico: ConversationTopic = None):
        """Agrega un mensaje al historial"""
        self.historial_mensajes.append({
            "rol": rol,
            "contenido": contenido,
            "topico": topico.value if topico else None,
            "timestamp": None  # Se agregaría con datetime
        })
        if topico and topico not in self.temas_discutidos:
            self.temas_discutidos.append(topico)
    
    def obtener_contexto_resumen(self) -> str:
        """Retorna un resumen del contexto para la siguiente respuesta"""
        return f"Usuario ha discutido: {', '.join([t.value for t in self.temas_discutidos])}"