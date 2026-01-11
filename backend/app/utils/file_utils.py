"""
Utilidades para manejo de archivos
"""
import os
import hashlib
import mimetypes
from typing import Optional, List, Tuple


# Tipos de archivo soportados
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/tiff': ['.tiff', '.tif'],
    'image/bmp': ['.bmp'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp']
}

SUPPORTED_DOCUMENT_TYPES = {
    'application/pdf': ['.pdf'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
}


def get_file_extension(filename: str) -> str:
    """Obtiene la extensión de un archivo"""
    return os.path.splitext(filename)[1].lower()


def get_mime_type(filename: str) -> Optional[str]:
    """Obtiene el tipo MIME de un archivo"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def is_supported_image(filename: str) -> bool:
    """Verifica si es una imagen soportada"""
    ext = get_file_extension(filename)
    for extensions in SUPPORTED_IMAGE_TYPES.values():
        if ext in extensions:
            return True
    return False


def is_supported_document(filename: str) -> bool:
    """Verifica si es un documento soportado para procesamiento"""
    ext = get_file_extension(filename)
    for extensions in SUPPORTED_DOCUMENT_TYPES.values():
        if ext in extensions:
            return True
    return is_supported_image(filename)


def is_template_file(filename: str) -> bool:
    """Verifica si es un archivo de plantilla válido"""
    ext = get_file_extension(filename)
    return ext in ['.xlsx', '.docx']


def calculate_file_hash(file_content: bytes) -> str:
    """Calcula el hash SHA-256 de un archivo"""
    return hashlib.sha256(file_content).hexdigest()


def get_file_size_mb(file_content: bytes) -> float:
    """Obtiene el tamaño del archivo en MB"""
    return len(file_content) / (1024 * 1024)


def validate_file_size(file_content: bytes, max_size_mb: int) -> Tuple[bool, str]:
    """
    Valida el tamaño del archivo
    
    Returns:
        Tupla (es_válido, mensaje)
    """
    size_mb = get_file_size_mb(file_content)
    if size_mb > max_size_mb:
        return False, f"Archivo muy grande: {size_mb:.2f}MB (máximo: {max_size_mb}MB)"
    return True, "OK"


def sanitize_filename(filename: str) -> str:
    """Limpia el nombre del archivo para uso seguro"""
    # Remover caracteres peligrosos
    dangerous_chars = ['..', '/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|']
    safe_name = filename
    
    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Limitar longitud
    if len(safe_name) > 200:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:200 - len(ext)] + ext
    
    return safe_name
