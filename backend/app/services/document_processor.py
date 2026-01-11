"""
Procesador principal de documentos
Coordina OCR, IA y procesamiento de plantillas
"""
import os
import uuid
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import aiofiles

from ..config import settings
from ..models.schemas import (
    DocumentUpload,
    ExtractionResult,
    ExtractionBatch,
    TemplateConfig,
    TemplateField,
    FieldMapping,
    ProcessingStatus
)
from .ocr_service import OCRService
from .ai_extractor import AIExtractorService
from .template_processor import TemplateProcessor


class DocumentProcessor:
    """
    Procesador principal que coordina:
    - Carga de documentos
    - Extracción de texto (OCR)
    - Extracción de datos (IA)
    - Generación de resultados
    """
    
    def __init__(self):
        """Inicializa el procesador de documentos"""
        self.ocr_service = OCRService()
        self.ai_extractor = AIExtractorService()
        self.template_processor = TemplateProcessor()
        self.upload_dir = settings.UPLOAD_DIR
        
        # Cache de lotes en procesamiento
        self._batches: Dict[str, ExtractionBatch] = {}
    
    async def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str
    ) -> DocumentUpload:
        """
        Guarda un archivo subido y crea el registro
        
        Args:
            file_content: Contenido del archivo
            filename: Nombre original del archivo
            
        Returns:
            Información del documento subido
        """
        # Generar ID único
        doc_id = str(uuid.uuid4())
        
        # Determinar tipo de archivo
        ext = os.path.splitext(filename)[1].lower()
        file_type = self._get_file_type(ext)
        
        # Crear ruta de guardado
        safe_filename = f"{doc_id}_{filename}"
        file_path = os.path.join(self.upload_dir, safe_filename)
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return DocumentUpload(
            id=doc_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=len(file_content),
            uploaded_at=datetime.now(),
            status=ProcessingStatus.PENDING
        )
    
    def _get_file_type(self, extension: str) -> str:
        """Determina el tipo de archivo por extensión"""
        image_exts = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
        pdf_exts = {'.pdf'}
        
        if extension in image_exts:
            return 'image'
        elif extension in pdf_exts:
            return 'pdf'
        else:
            return 'unknown'
    
    async def extract_text_from_document(
        self,
        document: DocumentUpload
    ) -> str:
        """
        Extrae texto de un documento usando OCR
        
        Args:
            document: Información del documento
            
        Returns:
            Texto extraído
        """
        try:
            if document.file_type == 'image':
                text = self.ocr_service.extract_text_from_image(document.file_path)
            elif document.file_type == 'pdf':
                pages = self.ocr_service.extract_text_from_pdf(document.file_path)
                text = "\n\n--- Página ---\n\n".join([page_text for _, page_text in pages])
            else:
                raise ValueError(f"Tipo de archivo no soportado: {document.file_type}")
            
            return text
            
        except Exception as e:
            raise Exception(f"Error extrayendo texto: {str(e)}")
    
    async def process_single_document(
        self,
        document: DocumentUpload,
        fields: List[TemplateField],
        use_ai: bool = True
    ) -> ExtractionResult:
        """
        Procesa un solo documento y extrae los campos
        
        Args:
            document: Documento a procesar
            fields: Campos a extraer
            use_ai: Si usar extracción con IA
            
        Returns:
            Resultado de extracción
        """
        start_time = datetime.now()
        
        try:
            # Intentar extracción directa con IA Vision si es imagen
            if use_ai and document.file_type == 'image':
                try:
                    field_mappings = await self.ai_extractor.extract_from_image(
                        document.file_path,
                        fields
                    )
                    
                    processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    # Calcular confianza promedio
                    confidences = [m.confidence for m in field_mappings.values() if m.confidence > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    return ExtractionResult(
                        document_id=document.id,
                        document_name=document.filename,
                        fields=field_mappings,
                        confidence_score=avg_confidence,
                        processing_time_ms=processing_time,
                        status=ProcessingStatus.COMPLETED
                    )
                except Exception as e:
                    # Fallback a OCR + text extraction
                    pass
            
            # Extraer texto con OCR
            extracted_text = await self.extract_text_from_document(document)
            
            # Extraer campos con IA
            if use_ai:
                field_mappings = await self.ai_extractor.extract_from_text(
                    extracted_text,
                    fields
                )
            else:
                field_mappings = self.ai_extractor.extract_without_ai(
                    extracted_text,
                    fields
                )
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Calcular confianza promedio
            confidences = [m.confidence for m in field_mappings.values() if m.confidence > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return ExtractionResult(
                document_id=document.id,
                document_name=document.filename,
                fields=field_mappings,
                raw_text=extracted_text,
                confidence_score=avg_confidence,
                processing_time_ms=processing_time,
                status=ProcessingStatus.COMPLETED
            )
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ExtractionResult(
                document_id=document.id,
                document_name=document.filename,
                fields={},
                processing_time_ms=processing_time,
                status=ProcessingStatus.ERROR,
                error_message=str(e)
            )
    
    async def process_batch(
        self,
        batch_id: str,
        documents: List[DocumentUpload],
        template_config: TemplateConfig,
        use_ai: bool = True,
        max_concurrent: int = 5
    ) -> ExtractionBatch:
        """
        Procesa un lote de documentos
        
        Args:
            batch_id: ID del lote
            documents: Lista de documentos
            template_config: Configuración de plantilla
            use_ai: Si usar extracción con IA
            max_concurrent: Máximo de documentos procesados concurrentemente
            
        Returns:
            Lote con resultados
        """
        batch = ExtractionBatch(
            id=batch_id,
            template_id=template_config.id,
            template_name=template_config.name,
            documents=documents,
            status=ProcessingStatus.PROCESSING,
            started_at=datetime.now(),
            total_documents=len(documents)
        )
        
        self._batches[batch_id] = batch
        
        # Procesar documentos con concurrencia limitada
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(doc):
            async with semaphore:
                return await self.process_single_document(doc, template_config.fields, use_ai)
        
        # Ejecutar procesamiento
        tasks = [process_with_semaphore(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for result in results:
            if isinstance(result, Exception):
                batch.results.append(ExtractionResult(
                    document_id="error",
                    document_name="Error",
                    fields={},
                    status=ProcessingStatus.ERROR,
                    error_message=str(result)
                ))
            else:
                batch.results.append(result)
                batch.processed_documents += 1
                if result.status == ProcessingStatus.COMPLETED:
                    batch.successful_extractions += 1
        
        batch.completed_at = datetime.now()
        batch.status = ProcessingStatus.COMPLETED if batch.successful_extractions > 0 else ProcessingStatus.ERROR
        
        return batch
    
    async def generate_output_file(
        self,
        batch: ExtractionBatch,
        template_config: TemplateConfig,
        output_format: str = "xlsx"
    ) -> str:
        """
        Genera el archivo de salida con los datos extraídos
        
        Args:
            batch: Lote con resultados
            template_config: Configuración de plantilla
            output_format: Formato de salida
            
        Returns:
            Ruta del archivo generado
        """
        successful_results = [r for r in batch.results if r.status == ProcessingStatus.COMPLETED]
        
        if not successful_results:
            raise ValueError("No hay resultados exitosos para exportar")
        
        if template_config.file_path and os.path.exists(template_config.file_path):
            # Usar plantilla existente
            output_path = self.template_processor.fill_excel_template(
                template_config.file_path,
                successful_results,
                template_config
            )
        else:
            # Crear nuevo Excel
            output_path = self.template_processor.export_results_to_excel(
                successful_results,
                template_config.fields
            )
        
        batch.output_file = output_path
        return output_path
    
    def get_batch_status(self, batch_id: str) -> Optional[ExtractionBatch]:
        """Obtiene el estado de un lote"""
        return self._batches.get(batch_id)
    
    def cleanup_document(self, document: DocumentUpload) -> bool:
        """Elimina un documento del sistema"""
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            return True
        except Exception:
            return False


# Instancia global
document_processor = DocumentProcessor()
