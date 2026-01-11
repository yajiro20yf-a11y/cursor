"""
Configuración de la aplicación DataExtractor AI
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Configuración de la API
    APP_NAME: str = "DataExtractor AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Rutas de archivos
    UPLOAD_DIR: str = "./uploads"
    TEMPLATES_DIR: str = "./templates"
    OUTPUT_DIR: str = "./outputs"
    
    # Configuración de OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-vision-preview"
    
    # Configuración de Tesseract OCR
    TESSERACT_CMD: Optional[str] = None
    TESSERACT_LANG: str = "spa+eng"
    
    # Límites
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILES_PER_BATCH: int = 50
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Crear directorios si no existen
for directory in [settings.UPLOAD_DIR, settings.TEMPLATES_DIR, settings.OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)
