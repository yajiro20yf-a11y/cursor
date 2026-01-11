package com.dataextractor.ai.data.models

import com.google.gson.annotations.SerializedName

/**
 * Tipos de campo soportados
 */
enum class FieldType {
    @SerializedName("text") TEXT,
    @SerializedName("number") NUMBER,
    @SerializedName("date") DATE,
    @SerializedName("email") EMAIL,
    @SerializedName("phone") PHONE,
    @SerializedName("address") ADDRESS,
    @SerializedName("currency") CURRENCY,
    @SerializedName("percentage") PERCENTAGE,
    @SerializedName("custom") CUSTOM
}

/**
 * Estado del procesamiento
 */
enum class ProcessingStatus {
    @SerializedName("pending") PENDING,
    @SerializedName("processing") PROCESSING,
    @SerializedName("completed") COMPLETED,
    @SerializedName("error") ERROR,
    @SerializedName("partial") PARTIAL
}

/**
 * Campo de plantilla
 */
data class TemplateField(
    val id: String,
    val name: String,
    @SerializedName("field_type")
    val fieldType: FieldType = FieldType.TEXT,
    val description: String? = null,
    @SerializedName("cell_reference")
    val cellReference: String? = null,
    @SerializedName("column_index")
    val columnIndex: Int? = null,
    val required: Boolean = false,
    @SerializedName("validation_pattern")
    val validationPattern: String? = null,
    val examples: List<String>? = null
)

/**
 * Mapeo de campo extraído
 */
data class FieldMapping(
    @SerializedName("field_id")
    val fieldId: String,
    @SerializedName("source_location")
    val sourceLocation: String? = null,
    val confidence: Float = 0f,
    @SerializedName("extracted_value")
    val extractedValue: Any? = null,
    val validated: Boolean = false
)

/**
 * Configuración de plantilla
 */
data class TemplateConfig(
    val id: String,
    val name: String,
    @SerializedName("file_path")
    val filePath: String,
    @SerializedName("file_type")
    val fileType: String,
    val fields: List<TemplateField> = emptyList(),
    @SerializedName("sheet_name")
    val sheetName: String? = null,
    @SerializedName("start_row")
    val startRow: Int = 2,
    @SerializedName("created_at")
    val createdAt: String? = null
)

/**
 * Análisis de plantilla
 */
data class TemplateAnalysis(
    @SerializedName("template_id")
    val templateId: String,
    @SerializedName("detected_fields")
    val detectedFields: List<TemplateField>,
    @SerializedName("suggested_mappings")
    val suggestedMappings: Map<String, String> = emptyMap(),
    @SerializedName("sheet_names")
    val sheetNames: List<String>? = null,
    @SerializedName("preview_data")
    val previewData: Map<String, Any>? = null
)

/**
 * Documento subido
 */
data class DocumentUpload(
    val id: String,
    val filename: String,
    @SerializedName("file_path")
    val filePath: String,
    @SerializedName("file_type")
    val fileType: String,
    @SerializedName("file_size")
    val fileSize: Long,
    @SerializedName("uploaded_at")
    val uploadedAt: String? = null,
    val status: ProcessingStatus = ProcessingStatus.PENDING,
    @SerializedName("extracted_text")
    val extractedText: String? = null,
    @SerializedName("error_message")
    val errorMessage: String? = null
)

/**
 * Resultado de extracción
 */
data class ExtractionResult(
    @SerializedName("document_id")
    val documentId: String,
    @SerializedName("document_name")
    val documentName: String,
    val fields: Map<String, FieldMapping> = emptyMap(),
    @SerializedName("raw_text")
    val rawText: String? = null,
    @SerializedName("confidence_score")
    val confidenceScore: Float = 0f,
    @SerializedName("processing_time_ms")
    val processingTimeMs: Int = 0,
    val status: ProcessingStatus = ProcessingStatus.PENDING,
    @SerializedName("error_message")
    val errorMessage: String? = null
)

/**
 * Lote de extracción
 */
data class ExtractionBatch(
    val id: String,
    @SerializedName("template_id")
    val templateId: String,
    @SerializedName("template_name")
    val templateName: String,
    val documents: List<DocumentUpload> = emptyList(),
    val results: List<ExtractionResult> = emptyList(),
    val status: ProcessingStatus = ProcessingStatus.PENDING,
    @SerializedName("started_at")
    val startedAt: String? = null,
    @SerializedName("completed_at")
    val completedAt: String? = null,
    @SerializedName("total_documents")
    val totalDocuments: Int = 0,
    @SerializedName("processed_documents")
    val processedDocuments: Int = 0,
    @SerializedName("successful_extractions")
    val successfulExtractions: Int = 0,
    @SerializedName("output_file")
    val outputFile: String? = null
)

/**
 * Respuesta de salud del servidor
 */
data class HealthResponse(
    val status: String,
    val version: String,
    val services: Map<String, String>
)
