from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.ocr_service import OCRService
from app.services.ai_extractor import AIExtractor
import shutil
import os
import json

router = APIRouter()
ocr_service = OCRService()
# En producción, la API KEY vendría de variables de entorno
ai_extractor = AIExtractor() 

@router.post("/upload-template")
async def upload_template(file: UploadFile = File(...), type: str = Form(...)):
    """
    Sube la plantilla maestra (Excel o Word) y devuelve su estructura.
    """
    file_location = f"documents/templates/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    return {
        "filename": file.filename, 
        "message": "Plantilla guardada correctamente.",
        "path": file_location
    }

@router.post("/process-batch")
async def process_batch(
    files: List[UploadFile] = File(...), 
    mapping_config: str = Form(...) 
):
    """
    1. Recibe imágenes.
    2. Aplica OCR (Texto crudo).
    3. Aplica IA (Datos estructurados).
    4. (Futuro) Rellena Excel.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos")

    # Parsear la configuración de mapeo que viene como string JSON desde el frontend
    # Ejemplo: {"campos_requeridos": ["Fecha", "Total", "Proveedor"]}
    try:
        config = json.loads(mapping_config)
        required_fields = config.get("campos_requeridos", ["Fecha", "Total", "Numero_Factura"]) # Default para pruebas
    except:
        required_fields = ["Fecha", "Total", "Numero_Factura"]

    results = []
    
    for file in files:
        content = await file.read()
        
        # 1. OCR
        extracted_text = ocr_service.extract_text_from_image(content)
        
        # 2. IA Extraction
        structured_data = ai_extractor.extract_structured_data(extracted_text, required_fields)
        
        results.append({
            "filename": file.filename,
            "raw_ocr": extracted_text[:50] + "...",
            "extracted_data": structured_data
        })
        
        # Guardar backup
        with open(f"documents/input/{file.filename}", "wb") as f:
            f.write(content)

    return {
        "status": "success",
        "processed_count": len(files),
        "data": results
    }
