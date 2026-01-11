from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter()

@router.post("/upload-template")
async def upload_template(file: UploadFile = File(...), type: str = Form(...)):
    """
    Sube la plantilla maestra (Excel o Word) y devuelve su estructura
    para que el frontend pueda permitir al usuario seleccionar campos.
    """
    return {"filename": file.filename, "message": "Plantilla recibida, analizando estructura..."}

@router.post("/process-batch")
async def process_batch(
    files: List[UploadFile] = File(...), 
    mapping_config: str = Form(...)
):
    """
    Recibe multiples archivos escaneados (fotos/pdfs) y la configuración de mapeo.
    Inicia el proceso de extracción OCR + IA.
    """
    return {"message": f"Procesando {len(files)} documentos", "status": "processing"}
