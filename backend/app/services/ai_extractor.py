import json
import os
from typing import List, Dict, Any

# Intentamos importar openai, si no está configurado, usaremos un mock
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AIExtractor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    def extract_structured_data(self, ocr_text: str, required_fields: List[str]) -> Dict[str, Any]:
        """
        Toma texto desordenado de OCR y busca campos específicos usando IA.
        Devuelve un diccionario JSON limpio.
        """
        if not ocr_text or len(ocr_text) < 5:
            return {}

        # Si no hay API Key configurada, devolvemos datos simulados para pruebas
        if not self.client:
            return self._mock_extraction(ocr_text, required_fields)

        prompt = self._build_prompt(ocr_text, required_fields)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # O gpt-4 para mayor precisión
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en extracción de datos de documentos OCR. Tu salida debe ser EXCLUSIVAMENTE un objeto JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Bajo para ser determinista y preciso
            )
            
            json_content = response.choices[0].message.content
            return self._parse_json_response(json_content)
        except Exception as e:
            print(f"Error en extracción IA: {e}")
            return {}

    def _build_prompt(self, text: str, fields: List[str]) -> str:
        return f"""
        Analiza el siguiente texto extraído de un documento escaneado (OCR).
        El texto puede contener errores de lectura.
        
        Extrae la información para los siguientes campos: {', '.join(fields)}.
        
        Reglas:
        1. Devuelve solo un JSON válido.
        2. Si no encuentras un dato, pon null o string vacío.
        3. Corrige errores evidentes de OCR (ej: 'F3cha' -> 'Fecha').
        
        Texto OCR:
        \"\"\"
        {text}
        \"\"\"
        """

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        try:
            # Limpiar posibles bloques de código markdown ```json ... ```
            clean_content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_content)
        except json.JSONDecodeError:
            print("Error parseando respuesta JSON de la IA")
            return {}

    def _mock_extraction(self, text: str, fields: List[str]) -> Dict[str, Any]:
        """
        Simulación para cuando no hay API Key real.
        Intenta buscar palabras clave simples.
        """
        print("⚠️ MODO SIMULACIÓN (Sin API Key de OpenAI) ⚠️")
        data = {}
        text_lower = text.lower()
        
        for field in fields:
            # Lógica muy tonta solo para demo: busca la palabra del campo y toma lo siguiente
            # En producción esto lo hace la IA real
            data[field] = f"[Valor simulado para {field}]"
            
        return data
