from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List
from app.services.ocr_service import OCRService
from app.services.ai_extractor import AIExtractor
from app.services.report_generator import ReportGenerator
import shutil
import os
import json
import zipfile
import io

router = APIRouter()
ocr_service = OCRService()
ai_extractor = AIExtractor() 
report_generator = ReportGenerator()

@router.post("/upload-template")
async def upload_template(file: UploadFile = File(...), type: str = Form(...)):
    """
    Sube la plantilla maestra (Excel o Word).
    """
    os.makedirs("documents/templates", exist_ok=True)
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
    mapping_config: str = Form(...),
    template_filename: str = Form(...) 
):
    """
    Flujo completo: Foto -> OCR -> IA -> Excel Relleno
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos")

    # Configuración de mapeo: {"NombreCliente": "B2", "Total": "F10"}
    try:
        config = json.loads(mapping_config)
        # Invertimos el mapa para saber qué buscar con la IA: ["NombreCliente", "Total"]
        ai_fields = list(config.keys())
    except:
        # Fallback para pruebas
        config = {"Fecha": "B2", "Total": "B3", "Proveedor": "B4"}
        ai_fields = list(config.keys())

    generated_files = []
    
    for file in files:
        # 1. Leer imagen
        content = await file.read()
        
        # 2. OCR
        extracted_text = ocr_service.extract_text_from_image(content)
        
        # 3. IA: Extraer datos semánticos (ej: encuentra el "Total")
        # Devuelve: {"Total": "500.00", "Fecha": "12/01/2023"}
        structured_data = ai_extractor.extract_structured_data(extracted_text, ai_fields)
        
        # 4. Mapeo final: Convertir "Total" -> "F10" para el Excel
        excel_data = {}
        for field_name, value in structured_data.items():
            if field_name in config:
                cell_address = config[field_name] # "F10"
                excel_data[cell_address] = value
        
        # 5. Generar Excel
        output_filename = f"Procesado_{file.filename}.xlsx"
        try:
            output_path = report_generator.generate_report(
                template_filename=template_filename,
                data=excel_data,
                output_filename=output_filename
            )
            generated_files.append(output_path)
        except Exception as e:
            print(f"Error generando reporte para {file.filename}: {e}")

    # Si se generó un solo archivo, devolverlo directo. Si son varios, crear un ZIP.
    if len(generated_files) == 1:
        return FileResponse(generated_files[0], filename=os.path.basename(generated_files[0]))
    elif len(generated_files) > 1:
        # Crear ZIP en memoria
        zip_filename = "Documentos_Procesados.zip"
        zip_path = f"documents/output/{zip_filename}"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in generated_files:
                zipf.write(file_path, os.path.basename(file_path))
        return FileResponse(zip_path, filename=zip_filename)
    else:
         return {"status": "error", "message": "No se pudieron generar archivos"}
