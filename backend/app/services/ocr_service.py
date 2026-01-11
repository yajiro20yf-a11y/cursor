import pytesseract
from PIL import Image
import io
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # En un entorno real, aquí verificaríamos si tesseract está instalado en el sistema
        pass

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Recibe los bytes de una imagen (jpg/png), la carga y extrae el texto usando Tesseract.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Pre-procesamiento básico para mejorar OCR (convertir a escala de grises)
            image = image.convert('L') 
            
            # Ejecutar OCR (asumimos español e inglés)
            # Nota: En producción necesitas tener instalado el binario de tesseract-ocr
            text = pytesseract.image_to_string(image, lang='spa+eng')
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error en OCR: {str(e)}")
            return ""

    def process_batch(self, images: list[bytes]) -> list[str]:
        """
        Procesa una lista de imágenes y devuelve una lista de textos extraídos.
        """
        results = []
        for img_bytes in images:
            text = self.extract_text_from_image(img_bytes)
            results.append(text)
        return results
