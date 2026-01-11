"""
Servicio de OCR para extraer texto de imágenes y PDFs
"""
import os
import io
from typing import Optional, List, Tuple
from PIL import Image
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import numpy as np
from ..config import settings


class OCRService:
    """
    Servicio de reconocimiento óptico de caracteres (OCR)
    Soporta imágenes (JPG, PNG, TIFF) y PDFs
    """
    
    def __init__(self):
        """Inicializa el servicio OCR"""
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        self.default_lang = settings.TESSERACT_LANG
        
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocesa la imagen para mejorar la precisión del OCR
        
        Args:
            image: Imagen PIL a procesar
            
        Returns:
            Imagen procesada
        """
        # Convertir a numpy array
        img_array = np.array(image)
        
        # Convertir a escala de grises si es necesario
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # Aplicar umbralización adaptativa
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Corregir inclinación (deskew)
        coords = np.column_stack(np.where(denoised > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(
                    denoised, M, (w, h),
                    flags=cv2.INTER_CUBIC, 
                    borderMode=cv2.BORDER_REPLICATE
                )
        
        return Image.fromarray(denoised)
    
    def extract_text_from_image(
        self, 
        image_path: str, 
        lang: Optional[str] = None,
        preprocess: bool = True
    ) -> str:
        """
        Extrae texto de una imagen
        
        Args:
            image_path: Ruta a la imagen
            lang: Idioma para OCR (por defecto: español + inglés)
            preprocess: Si aplicar preprocesamiento
            
        Returns:
            Texto extraído
        """
        lang = lang or self.default_lang
        
        try:
            image = Image.open(image_path)
            
            if preprocess:
                image = self.preprocess_image(image)
            
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error al procesar imagen: {str(e)}")
    
    def extract_text_from_image_bytes(
        self, 
        image_bytes: bytes,
        lang: Optional[str] = None,
        preprocess: bool = True
    ) -> str:
        """
        Extrae texto de bytes de imagen
        
        Args:
            image_bytes: Bytes de la imagen
            lang: Idioma para OCR
            preprocess: Si aplicar preprocesamiento
            
        Returns:
            Texto extraído
        """
        lang = lang or self.default_lang
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if preprocess:
                image = self.preprocess_image(image)
            
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error al procesar imagen: {str(e)}")
    
    def extract_text_from_pdf(
        self, 
        pdf_path: str,
        lang: Optional[str] = None,
        dpi: int = 300
    ) -> List[Tuple[int, str]]:
        """
        Extrae texto de un PDF escaneado
        
        Args:
            pdf_path: Ruta al archivo PDF
            lang: Idioma para OCR
            dpi: Resolución para conversión de PDF
            
        Returns:
            Lista de tuplas (número de página, texto)
        """
        lang = lang or self.default_lang
        results = []
        
        try:
            # Convertir PDF a imágenes
            images = convert_from_path(pdf_path, dpi=dpi)
            
            for i, image in enumerate(images, 1):
                # Preprocesar imagen
                processed = self.preprocess_image(image)
                
                # Extraer texto
                text = pytesseract.image_to_string(processed, lang=lang)
                results.append((i, text.strip()))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error al procesar PDF: {str(e)}")
    
    def extract_text_from_pdf_bytes(
        self, 
        pdf_bytes: bytes,
        lang: Optional[str] = None,
        dpi: int = 300
    ) -> List[Tuple[int, str]]:
        """
        Extrae texto de bytes de PDF
        
        Args:
            pdf_bytes: Bytes del PDF
            lang: Idioma para OCR
            dpi: Resolución para conversión
            
        Returns:
            Lista de tuplas (número de página, texto)
        """
        lang = lang or self.default_lang
        results = []
        
        try:
            images = convert_from_bytes(pdf_bytes, dpi=dpi)
            
            for i, image in enumerate(images, 1):
                processed = self.preprocess_image(image)
                text = pytesseract.image_to_string(processed, lang=lang)
                results.append((i, text.strip()))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error al procesar PDF: {str(e)}")
    
    def extract_with_bounding_boxes(
        self, 
        image_path: str,
        lang: Optional[str] = None
    ) -> dict:
        """
        Extrae texto con información de ubicación (bounding boxes)
        
        Args:
            image_path: Ruta a la imagen
            lang: Idioma para OCR
            
        Returns:
            Diccionario con texto y coordenadas
        """
        lang = lang or self.default_lang
        
        try:
            image = Image.open(image_path)
            image = self.preprocess_image(image)
            
            # Obtener datos detallados
            data = pytesseract.image_to_data(
                image, lang=lang, output_type=pytesseract.Output.DICT
            )
            
            # Estructurar resultados
            results = {
                "full_text": "",
                "words": [],
                "lines": [],
                "blocks": []
            }
            
            current_line = {"text": "", "words": [], "bbox": None}
            current_block = {"text": "", "lines": [], "bbox": None}
            
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                if not text:
                    continue
                    
                word_info = {
                    "text": text,
                    "confidence": data["conf"][i],
                    "bbox": {
                        "x": data["left"][i],
                        "y": data["top"][i],
                        "width": data["width"][i],
                        "height": data["height"][i]
                    },
                    "line_num": data["line_num"][i],
                    "block_num": data["block_num"][i]
                }
                
                results["words"].append(word_info)
                results["full_text"] += text + " "
            
            results["full_text"] = results["full_text"].strip()
            return results
            
        except Exception as e:
            raise Exception(f"Error al procesar imagen con bounding boxes: {str(e)}")
    
    def get_supported_languages(self) -> List[str]:
        """Obtiene la lista de idiomas soportados por Tesseract"""
        try:
            return pytesseract.get_languages()
        except Exception:
            return ["eng", "spa"]  # Idiomas por defecto


# Instancia global del servicio
ocr_service = OCRService()
