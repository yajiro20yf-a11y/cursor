"""
Servicio de extracción de datos usando IA (OpenAI GPT-4 Vision)
"""
import json
import base64
import re
from typing import Optional, List, Dict, Any
from openai import OpenAI
from ..config import settings
from ..models.schemas import TemplateField, FieldType, FieldMapping


class AIExtractorService:
    """
    Servicio de extracción inteligente de datos usando IA
    Utiliza GPT-4 Vision para analizar imágenes y texto
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de extracción con IA
        
        Args:
            api_key: Clave de API de OpenAI (opcional, usa configuración por defecto)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def _build_extraction_prompt(
        self, 
        fields: List[TemplateField],
        additional_context: Optional[str] = None
    ) -> str:
        """
        Construye el prompt para la extracción de datos
        
        Args:
            fields: Lista de campos a extraer
            additional_context: Contexto adicional
            
        Returns:
            Prompt formateado
        """
        fields_description = []
        
        for field in fields:
            field_info = f"- **{field.name}** (ID: {field.id})"
            field_info += f"\n  - Tipo: {field.field_type.value}"
            
            if field.description:
                field_info += f"\n  - Descripción: {field.description}"
            
            if field.examples:
                field_info += f"\n  - Ejemplos: {', '.join(field.examples)}"
            
            if field.required:
                field_info += "\n  - Campo OBLIGATORIO"
                
            fields_description.append(field_info)
        
        prompt = f"""Eres un experto en extracción de datos de documentos. Analiza el documento proporcionado y extrae la información solicitada.

## CAMPOS A EXTRAER:
{chr(10).join(fields_description)}

## INSTRUCCIONES:
1. Analiza cuidadosamente el documento (imagen o texto)
2. Identifica y extrae cada campo solicitado
3. Si un campo no se encuentra, indica null
4. Proporciona un nivel de confianza (0.0 a 1.0) para cada extracción
5. Mantén el formato original de los datos cuando sea posible

## FORMATO DE RESPUESTA:
Responde ÚNICAMENTE con un JSON válido con la siguiente estructura:
{{
    "extractions": {{
        "<field_id>": {{
            "value": "<valor extraído o null>",
            "confidence": <0.0 a 1.0>,
            "source_location": "<ubicación aproximada en el documento>"
        }}
    }},
    "document_type": "<tipo de documento detectado>",
    "language": "<idioma del documento>",
    "notes": "<observaciones adicionales>"
}}
"""
        
        if additional_context:
            prompt += f"\n## CONTEXTO ADICIONAL:\n{additional_context}"
        
        return prompt
    
    def _parse_field_value(self, value: Any, field_type: FieldType) -> Any:
        """
        Parsea y valida el valor extraído según el tipo de campo
        
        Args:
            value: Valor extraído
            field_type: Tipo de campo esperado
            
        Returns:
            Valor parseado
        """
        if value is None:
            return None
            
        try:
            if field_type == FieldType.NUMBER:
                # Limpiar y convertir a número
                cleaned = re.sub(r'[^\d.,\-]', '', str(value))
                cleaned = cleaned.replace(',', '.')
                return float(cleaned) if '.' in cleaned else int(cleaned)
                
            elif field_type == FieldType.CURRENCY:
                # Extraer valor numérico de moneda
                cleaned = re.sub(r'[^\d.,\-]', '', str(value))
                cleaned = cleaned.replace(',', '.')
                return float(cleaned)
                
            elif field_type == FieldType.PERCENTAGE:
                # Convertir porcentaje
                cleaned = re.sub(r'[^\d.,\-]', '', str(value))
                cleaned = cleaned.replace(',', '.')
                return float(cleaned)
                
            elif field_type == FieldType.DATE:
                # Mantener como string para flexibilidad
                return str(value).strip()
                
            elif field_type == FieldType.EMAIL:
                # Validar formato básico de email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                match = re.search(email_pattern, str(value))
                return match.group() if match else str(value).strip()
                
            elif field_type == FieldType.PHONE:
                # Limpiar número de teléfono
                return re.sub(r'[^\d+\-\s()]', '', str(value)).strip()
                
            else:
                return str(value).strip()
                
        except Exception:
            return str(value).strip() if value else None
    
    async def extract_from_text(
        self,
        text: str,
        fields: List[TemplateField],
        additional_context: Optional[str] = None
    ) -> Dict[str, FieldMapping]:
        """
        Extrae datos de texto usando IA
        
        Args:
            text: Texto del documento
            fields: Campos a extraer
            additional_context: Contexto adicional
            
        Returns:
            Diccionario de campos extraídos
        """
        if not self.client:
            raise ValueError("Cliente de OpenAI no configurado. Proporcione OPENAI_API_KEY.")
        
        prompt = self._build_extraction_prompt(fields, additional_context)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"Extrae los datos del siguiente documento:\n\n{text}"
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._process_extraction_result(result, fields)
            
        except Exception as e:
            raise Exception(f"Error en extracción con IA: {str(e)}")
    
    async def extract_from_image(
        self,
        image_path: str,
        fields: List[TemplateField],
        additional_context: Optional[str] = None
    ) -> Dict[str, FieldMapping]:
        """
        Extrae datos directamente de una imagen usando GPT-4 Vision
        
        Args:
            image_path: Ruta a la imagen
            fields: Campos a extraer
            additional_context: Contexto adicional
            
        Returns:
            Diccionario de campos extraídos
        """
        if not self.client:
            raise ValueError("Cliente de OpenAI no configurado. Proporcione OPENAI_API_KEY.")
        
        # Leer y codificar imagen
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Detectar tipo de imagen
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        else:
            mime_type = "image/png"
        
        prompt = self._build_extraction_prompt(fields, additional_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen de documento y extrae los datos solicitados."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )
            
            # Parsear respuesta JSON
            content = response.choices[0].message.content
            
            # Intentar extraer JSON del contenido
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            return self._process_extraction_result(result, fields)
            
        except Exception as e:
            raise Exception(f"Error en extracción de imagen con IA: {str(e)}")
    
    async def extract_from_image_bytes(
        self,
        image_bytes: bytes,
        fields: List[TemplateField],
        mime_type: str = "image/png",
        additional_context: Optional[str] = None
    ) -> Dict[str, FieldMapping]:
        """
        Extrae datos de bytes de imagen
        
        Args:
            image_bytes: Bytes de la imagen
            fields: Campos a extraer
            mime_type: Tipo MIME de la imagen
            additional_context: Contexto adicional
            
        Returns:
            Diccionario de campos extraídos
        """
        if not self.client:
            raise ValueError("Cliente de OpenAI no configurado.")
        
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        prompt = self._build_extraction_prompt(fields, additional_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analiza esta imagen de documento y extrae los datos solicitados."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            return self._process_extraction_result(result, fields)
            
        except Exception as e:
            raise Exception(f"Error en extracción: {str(e)}")
    
    def _process_extraction_result(
        self,
        result: dict,
        fields: List[TemplateField]
    ) -> Dict[str, FieldMapping]:
        """
        Procesa el resultado de la extracción y lo convierte a FieldMappings
        
        Args:
            result: Resultado JSON de la IA
            fields: Campos originales
            
        Returns:
            Diccionario de FieldMappings
        """
        field_mappings = {}
        extractions = result.get("extractions", {})
        
        # Crear mapa de tipos de campo
        field_types = {f.id: f.field_type for f in fields}
        
        for field in fields:
            field_data = extractions.get(field.id, {})
            
            if isinstance(field_data, dict):
                raw_value = field_data.get("value")
                confidence = field_data.get("confidence", 0.0)
                source_location = field_data.get("source_location")
            else:
                raw_value = field_data
                confidence = 0.5
                source_location = None
            
            # Parsear valor según tipo
            parsed_value = self._parse_field_value(
                raw_value, 
                field_types.get(field.id, FieldType.TEXT)
            )
            
            field_mappings[field.id] = FieldMapping(
                field_id=field.id,
                extracted_value=parsed_value,
                confidence=float(confidence) if confidence else 0.0,
                source_location=source_location,
                validated=False
            )
        
        return field_mappings
    
    def extract_without_ai(
        self,
        text: str,
        fields: List[TemplateField]
    ) -> Dict[str, FieldMapping]:
        """
        Extracción básica sin IA usando patrones regex
        Útil como fallback cuando no hay API de OpenAI
        
        Args:
            text: Texto del documento
            fields: Campos a extraer
            
        Returns:
            Diccionario de campos extraídos
        """
        field_mappings = {}
        
        # Patrones comunes
        patterns = {
            FieldType.EMAIL: r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            FieldType.PHONE: r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            FieldType.DATE: r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',
            FieldType.CURRENCY: r'[\$€£¥]\s*[\d,]+\.?\d*|\d+[,.]?\d*\s*(?:USD|EUR|MXN|pesos?|dólares?)',
            FieldType.PERCENTAGE: r'\d+[.,]?\d*\s*%',
            FieldType.NUMBER: r'\b\d+[.,]?\d*\b'
        }
        
        for field in fields:
            value = None
            confidence = 0.0
            
            # Buscar por nombre del campo en el texto
            field_pattern = rf'{re.escape(field.name)}[:\s]+(.+?)(?:\n|$)'
            match = re.search(field_pattern, text, re.IGNORECASE)
            
            if match:
                value = match.group(1).strip()
                confidence = 0.7
            else:
                # Buscar por tipo de campo
                type_pattern = patterns.get(field.field_type)
                if type_pattern:
                    matches = re.findall(type_pattern, text)
                    if matches:
                        value = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        confidence = 0.5
            
            # Parsear valor
            parsed_value = self._parse_field_value(value, field.field_type)
            
            field_mappings[field.id] = FieldMapping(
                field_id=field.id,
                extracted_value=parsed_value,
                confidence=confidence,
                source_location=None,
                validated=False
            )
        
        return field_mappings


# Instancia global del servicio
ai_extractor = AIExtractorService()
