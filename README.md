# DocuFill AI - Extractor y Rellenador Inteligente de Documentos

## Descripción
Esta aplicación permite automatizar el llenado de plantillas (Excel/Word) extrayendo datos de múltiples fuentes (PDFs escaneados, imágenes) utilizando Inteligencia Artificial, manteniendo el formato original de la plantilla.

## Arquitectura del Sistema

### 1. Frontend (Interfaz de Usuario)
- **Tecnología:** React / Next.js
- **Funciones:**
  - Subida de Plantilla (Master Template).
  - Interfaz de "Mapeo": El usuario define qué celdas/lugares de la plantilla recibirán datos (ej: Celda B2 = "Nombre del Cliente").
  - Subida de Lotes: Carga de múltiples PDFs/Imágenes fuente.
  - Panel de Revisión: Verificación de los datos extraídos por la IA antes de generar los archivos.

### 2. Backend (API & Procesamiento)
- **Tecnología:** Python (FastAPI)
- **Módulos:**
  - `DocumentParser`: Lee archivos Word (.docx) y Excel (.xlsx) preservando estilos.
  - `OCRService`: Convierte imágenes escaneadas a texto plano (usando Tesseract o Cloud Vision).
  - `AIExtractor`: Usa LLMs (GPT/Claude/Llama) para entender el texto desordenado y convertirlo a JSON estructurado basado en los campos que pidió el usuario.
  - `ReportGenerator`: Inyecta el JSON en la plantilla original sin romper el diseño.

## Flujo de Trabajo

1. **Configuración de Plantilla:**
   - El usuario sube `Plantilla.xlsx`.
   - El usuario indica: "En la celda B5 va el 'Total de la Factura'".
   
2. **Ingesta de Datos:**
   - El usuario sube 50 imágenes de facturas escaneadas.
   
3. **Procesamiento IA:**
   - El sistema aplica OCR a cada imagen.
   - La IA busca "Total de la Factura" en el texto extraído, aunque esté en diferentes lugares en cada foto.
   
4. **Generación:**
   - El sistema toma `Plantilla.xlsx` y genera 50 archivos (o uno consolidado) con los datos rellenos, respetando colores, bordes y fuentes.

## Estructura de Carpetas

- `/backend`: Lógica del servidor y procesamiento de archivos.
- `/frontend`: Interfaz web.
- `/documents`: Almacenamiento temporal de archivos (en producción sería S3/Azure Blob).
