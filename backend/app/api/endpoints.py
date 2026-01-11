from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.ocr_service import OCRService
import shutil
import os

router = APIRouter()
ocr_service = OCRService()

@router.post("/upload-template")
async def upload_template(file: UploadFile = File(...), type: str = Form(...)):
    """
    Sube la plantilla maestra (Excel o Word) y devuelve su estructura.
    """
    # Guardar plantilla temporalmente
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
    # mapping_config: str = Form(...) # Opcional por ahora para pruebas
):
    """
    Recibe archivos escaneados desde la App Móvil, ejecuta OCR y devuelve el texto crudo.
    En el futuro, esto pasará a la capa de IA para estructuración.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos")

    results = []
    
    for file in files:
        # Leer contenido del archivo en memoria
        content = await file.read()
        
        # Ejecutar OCR
        extracted_text = ocr_service.extract_text_from_image(content)
        
        # Simulación de extracción de datos (La "IA" básica)
        # Aquí buscaríamos patrones específicos si tuviéramos el mapping
        
        results.append({
            "filename": file.filename,
            "raw_text_preview": extracted_text[:100] + "..." if extracted_text else "No text detected",
            "full_text": extracted_text
        })
        
        # Guardar copia de seguridad de la imagen
        with open(f"documents/input/{file.filename}", "wb") as f:
            f.write(content)

    return {
        "status": "success",
        "processed_count": len(files),
        "data": results
    }
