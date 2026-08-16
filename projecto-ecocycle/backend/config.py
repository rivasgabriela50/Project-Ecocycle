"""
Configuración de la aplicación Ecocycle
"""

import os
from datetime import timedelta


class Config:
    """Configuración base de la aplicación"""
    
    # Información general
    APP_NAME = "Ecocycle"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///ecocycle.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "ecocycle-dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "ecocycle-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Rutas
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB máximo
    
    # Métricas de impacto (valores por defecto)
    DEFAULT_METRICS = {
        "energia_ahorrada_kwh": 0,
        "emisiones_reducidas_kg": 0,
        "eficiencia_porcentaje": 0,
        "autonomia_horas": 0
    }
    
    # Configuración de modelos ML
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models")
    CLASSIFIER_MODEL = "classifier_model.pkl"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "ecocycle.log")


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Selector de configuración
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config(env=None):
    """Obtiene la configuración según el ambiente"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config_dict.get(env, config_dict["default"])