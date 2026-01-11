"""
Rutas de la API REST para DataExtractor AI
"""
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse

from ..config import settings
from ..models.schemas import (
    TemplateField,
    TemplateConfig,
    DocumentUpload,
    ExtractionResult,
    ExtractionBatch,
    TemplateAnalysis,
    ExtractionRequest,
    ProcessingStatus,
    FieldType
)
from ..services.document_processor import document_processor
from ..services.template_processor import template_processor
from ..utils.file_utils import (
    is_supported_document,
    is_template_file,
    validate_file_size,
    sanitize_filename
)


router = APIRouter()


# ============= PLANTILLAS =============

@router.post("/templates/upload", response_model=TemplateAnalysis)
async def upload_template(
    file: UploadFile = File(...),
    template_name: Optional[str] = Form(None)
):
    """
    Sube una plantilla Excel o Word y analiza su estructura
    """
    # Validar tipo de archivo
    if not is_template_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no soportado. Use .xlsx o .docx"
        )
    
    # Leer contenido
    content = await file.read()
    
    # Validar tamaño
    is_valid, msg = validate_file_size(content, settings.MAX_FILE_SIZE_MB)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # Guardar archivo
    template_id = str(uuid.uuid4())
    safe_name = sanitize_filename(file.filename)
    file_path = os.path.join(settings.TEMPLATES_DIR, f"{template_id}_{safe_name}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Analizar plantilla
    try:
        if file.filename.endswith('.xlsx'):
            analysis = template_processor.analyze_excel_template(file_path)
        else:
            analysis = template_processor.analyze_word_template(file_path)
        
        analysis.template_id = template_id
        return analysis
        
    except Exception as e:
        # Limpiar archivo si falla
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error analizando plantilla: {str(e)}")


@router.post("/templates/configure", response_model=TemplateConfig)
async def configure_template(
    template_id: str = Form(...),
    template_name: str = Form(...),
    fields: str = Form(...),  # JSON string of TemplateField list
    sheet_name: Optional[str] = Form(None),
    start_row: int = Form(2)
):
    """
    Configura los campos a extraer para una plantilla
    """
    import json
    
    # Buscar archivo de plantilla
    template_files = [f for f in os.listdir(settings.TEMPLATES_DIR) if f.startswith(template_id)]
    if not template_files:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    file_path = os.path.join(settings.TEMPLATES_DIR, template_files[0])
    file_type = "xlsx" if file_path.endswith('.xlsx') else "docx"
    
    # Parsear campos
    try:
        fields_data = json.loads(fields)
        template_fields = [TemplateField(**f) for f in fields_data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en formato de campos: {str(e)}")
    
    return TemplateConfig(
        id=template_id,
        name=template_name,
        file_path=file_path,
        file_type=file_type,
        fields=template_fields,
        sheet_name=sheet_name,
        start_row=start_row
    )


@router.get("/templates/{template_id}/analyze", response_model=TemplateAnalysis)
async def analyze_template(template_id: str, sheet_name: Optional[str] = None):
    """
    Re-analiza una plantilla existente
    """
    template_files = [f for f in os.listdir(settings.TEMPLATES_DIR) if f.startswith(template_id)]
    if not template_files:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    
    file_path = os.path.join(settings.TEMPLATES_DIR, template_files[0])
    
    if file_path.endswith('.xlsx'):
        return template_processor.analyze_excel_template(file_path, sheet_name)
    else:
        return template_processor.analyze_word_template(file_path)


# ============= DOCUMENTOS =============

@router.post("/documents/upload", response_model=List[DocumentUpload])
async def upload_documents(
    files: List[UploadFile] = File(...)
):
    """
    Sube múltiples documentos (imágenes o PDFs) para procesar
    """
    if len(files) > settings.MAX_FILES_PER_BATCH:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo {settings.MAX_FILES_PER_BATCH} archivos por lote"
        )
    
    uploaded_documents = []
    
    for file in files:
        # Validar tipo
        if not is_supported_document(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo no soportado: {file.filename}"
            )
        
        # Leer contenido
        content = await file.read()
        
        # Validar tamaño
        is_valid, msg = validate_file_size(content, settings.MAX_FILE_SIZE_MB)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"{file.filename}: {msg}")
        
        # Guardar documento
        doc = await document_processor.save_uploaded_file(content, file.filename)
        uploaded_documents.append(doc)
    
    return uploaded_documents


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Elimina un documento subido
    """
    # Buscar archivo
    for filename in os.listdir(settings.UPLOAD_DIR):
        if filename.startswith(document_id):
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            os.remove(file_path)
            return {"message": "Documento eliminado", "id": document_id}
    
    raise HTTPException(status_code=404, detail="Documento no encontrado")


# ============= EXTRACCIÓN =============

@router.post("/extraction/process", response_model=ExtractionBatch)
async def process_extraction(
    template_config: TemplateConfig,
    document_ids: List[str],
    use_ai: bool = True
):
    """
    Procesa la extracción de datos de múltiples documentos
    """
    # Reconstruir lista de documentos
    documents = []
    for doc_id in document_ids:
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.startswith(doc_id):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                original_name = "_".join(filename.split("_")[1:])
                
                ext = os.path.splitext(filename)[1].lower()
                file_type = 'image' if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp'] else 'pdf'
                
                documents.append(DocumentUpload(
                    id=doc_id,
                    filename=original_name,
                    file_path=file_path,
                    file_type=file_type,
                    file_size=os.path.getsize(file_path),
                    status=ProcessingStatus.PENDING
                ))
                break
    
    if not documents:
        raise HTTPException(status_code=404, detail="No se encontraron documentos")
    
    # Procesar lote
    batch_id = str(uuid.uuid4())
    
    try:
        batch = await document_processor.process_batch(
            batch_id,
            documents,
            template_config,
            use_ai=use_ai
        )
        return batch
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento: {str(e)}")


@router.post("/extraction/single", response_model=ExtractionResult)
async def process_single_document(
    document_id: str = Form(...),
    fields: str = Form(...),  # JSON string
    use_ai: bool = Form(True)
):
    """
    Procesa un solo documento y extrae campos
    """
    import json
    
    # Buscar documento
    document = None
    for filename in os.listdir(settings.UPLOAD_DIR):
        if filename.startswith(document_id):
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            original_name = "_".join(filename.split("_")[1:])
            
            ext = os.path.splitext(filename)[1].lower()
            file_type = 'image' if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp'] else 'pdf'
            
            document = DocumentUpload(
                id=document_id,
                filename=original_name,
                file_path=file_path,
                file_type=file_type,
                file_size=os.path.getsize(file_path),
                status=ProcessingStatus.PENDING
            )
            break
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Parsear campos
    try:
        fields_data = json.loads(fields)
        template_fields = [TemplateField(**f) for f in fields_data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en formato de campos: {str(e)}")
    
    # Procesar
    try:
        result = await document_processor.process_single_document(
            document,
            template_fields,
            use_ai=use_ai
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento: {str(e)}")


@router.get("/extraction/batch/{batch_id}", response_model=ExtractionBatch)
async def get_batch_status(batch_id: str):
    """
    Obtiene el estado de un lote de extracción
    """
    batch = document_processor.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return batch


# ============= EXPORTACIÓN =============

@router.post("/export/excel")
async def export_to_excel(
    batch_id: str = Form(...),
    template_config: str = Form(...)  # JSON string
):
    """
    Exporta los resultados de extracción a Excel
    """
    import json
    
    # Obtener lote
    batch = document_processor.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Parsear configuración
    try:
        config_data = json.loads(template_config)
        config = TemplateConfig(**config_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en configuración: {str(e)}")
    
    # Generar archivo
    try:
        output_path = await document_processor.generate_output_file(batch, config)
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(output_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando archivo: {str(e)}")


@router.post("/export/results")
async def export_results_directly(
    results: str = Form(...),  # JSON string of List[ExtractionResult]
    fields: str = Form(...)    # JSON string of List[TemplateField]
):
    """
    Exporta resultados directamente a Excel sin usar lote
    """
    import json
    
    try:
        results_data = json.loads(results)
        extraction_results = [ExtractionResult(**r) for r in results_data]
        
        fields_data = json.loads(fields)
        template_fields = [TemplateField(**f) for f in fields_data]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en datos: {str(e)}")
    
    try:
        output_path = template_processor.export_results_to_excel(
            extraction_results,
            template_fields
        )
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(output_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando archivo: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Descarga un archivo generado
    """
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        file_path,
        filename=filename
    )


# ============= UTILIDADES =============

@router.get("/health")
async def health_check():
    """
    Verifica el estado del servicio
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "ocr": "available",
            "ai": "available" if settings.OPENAI_API_KEY else "not_configured"
        }
    }


@router.get("/field-types")
async def get_field_types():
    """
    Obtiene los tipos de campo disponibles
    """
    return [
        {"value": ft.value, "label": ft.value.replace("_", " ").title()}
        for ft in FieldType
    ]
