"""
Esquemas de datos para la aplicación DataExtractor AI
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class FieldType(str, Enum):
    """Tipos de campos soportados"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    CUSTOM = "custom"


class ProcessingStatus(str, Enum):
    """Estados del procesamiento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    PARTIAL = "partial"


class TemplateField(BaseModel):
    """Define un campo a extraer de los documentos"""
    id: str = Field(..., description="Identificador único del campo")
    name: str = Field(..., description="Nombre del campo")
    field_type: FieldType = Field(default=FieldType.TEXT, description="Tipo de dato del campo")
    description: Optional[str] = Field(None, description="Descripción del campo para ayudar a la IA")
    cell_reference: Optional[str] = Field(None, description="Referencia de celda en Excel (ej: A1, B2)")
    column_index: Optional[int] = Field(None, description="Índice de columna para datos tabulares")
    required: bool = Field(default=False, description="Si el campo es obligatorio")
    validation_pattern: Optional[str] = Field(None, description="Patrón regex para validación")
    examples: Optional[List[str]] = Field(None, description="Ejemplos del tipo de dato esperado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "nombre_cliente",
                "name": "Nombre del Cliente",
                "field_type": "text",
                "description": "Nombre completo del cliente",
                "cell_reference": "B2",
                "required": True,
                "examples": ["Juan Pérez", "María García"]
            }
        }


class FieldMapping(BaseModel):
    """Mapeo de un campo de plantilla a datos extraídos"""
    field_id: str
    source_location: Optional[str] = Field(None, description="Ubicación en el documento fuente")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extracted_value: Optional[Any] = None
    validated: bool = False


class TemplateConfig(BaseModel):
    """Configuración de una plantilla"""
    id: str = Field(..., description="ID único de la plantilla")
    name: str = Field(..., description="Nombre de la plantilla")
    file_path: str = Field(..., description="Ruta del archivo de plantilla")
    file_type: str = Field(..., description="Tipo de archivo (xlsx, docx)")
    fields: List[TemplateField] = Field(default_factory=list)
    sheet_name: Optional[str] = Field(None, description="Nombre de hoja para Excel")
    start_row: int = Field(default=1, description="Fila inicial para datos")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "factura_template",
                "name": "Plantilla de Facturas",
                "file_path": "/templates/facturas.xlsx",
                "file_type": "xlsx",
                "sheet_name": "Datos",
                "start_row": 2
            }
        }


class DocumentUpload(BaseModel):
    """Información de un documento subido"""
    id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.PENDING
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None


class ExtractionResult(BaseModel):
    """Resultado de extracción de un documento"""
    document_id: str
    document_name: str
    fields: Dict[str, FieldMapping]
    raw_text: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_time_ms: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    

class ExtractionBatch(BaseModel):
    """Lote de extracción de múltiples documentos"""
    id: str
    template_id: str
    template_name: str
    documents: List[DocumentUpload]
    results: List[ExtractionResult] = Field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_documents: int = 0
    processed_documents: int = 0
    successful_extractions: int = 0
    output_file: Optional[str] = None


class TemplateAnalysis(BaseModel):
    """Resultado del análisis de una plantilla"""
    template_id: str
    detected_fields: List[TemplateField]
    suggested_mappings: Dict[str, str]
    sheet_names: Optional[List[str]] = None
    preview_data: Optional[Dict[str, Any]] = None


class ExtractionRequest(BaseModel):
    """Solicitud de extracción de datos"""
    template_id: str
    document_ids: List[str]
    fields_to_extract: List[str] = Field(default_factory=list, description="IDs de campos a extraer, vacío = todos")
    use_ai_enhancement: bool = True
    language: str = "es"


class ExtractionPreview(BaseModel):
    """Vista previa de extracción antes de confirmar"""
    batch_id: str
    results: List[ExtractionResult]
    template_preview: Dict[str, Any]
    estimated_confidence: float
