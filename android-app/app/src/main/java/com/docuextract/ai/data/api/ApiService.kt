package com.docuextract.ai.data.api

import com.docuextract.ai.data.models.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.*

/**
 * Interfaz de la API del servidor
 */
interface ApiService {

    // ============= PLANTILLAS =============

    /**
     * Sube y analiza una plantilla
     */
    @Multipart
    @POST("templates/upload")
    suspend fun uploadTemplate(
        @Part file: MultipartBody.Part,
        @Part("template_name") templateName: RequestBody? = null
    ): Response<TemplateAnalysis>

    /**
     * Configura los campos de una plantilla
     */
    @FormUrlEncoded
    @POST("templates/configure")
    suspend fun configureTemplate(
        @Field("template_id") templateId: String,
        @Field("template_name") templateName: String,
        @Field("fields") fields: String,  // JSON string
        @Field("sheet_name") sheetName: String? = null,
        @Field("start_row") startRow: Int = 2
    ): Response<TemplateConfig>

    /**
     * Re-analiza una plantilla existente
     */
    @GET("templates/{templateId}/analyze")
    suspend fun analyzeTemplate(
        @Path("templateId") templateId: String,
        @Query("sheet_name") sheetName: String? = null
    ): Response<TemplateAnalysis>

    // ============= DOCUMENTOS =============

    /**
     * Sube múltiples documentos
     */
    @Multipart
    @POST("documents/upload")
    suspend fun uploadDocuments(
        @Part files: List<MultipartBody.Part>
    ): Response<List<DocumentUpload>>

    /**
     * Elimina un documento
     */
    @DELETE("documents/{documentId}")
    suspend fun deleteDocument(
        @Path("documentId") documentId: String
    ): Response<Unit>

    // ============= EXTRACCIÓN =============

    /**
     * Procesa un lote de documentos
     */
    @POST("extraction/process")
    suspend fun processExtraction(
        @Body request: ExtractionRequest
    ): Response<ExtractionBatch>

    /**
     * Procesa un solo documento
     */
    @FormUrlEncoded
    @POST("extraction/single")
    suspend fun processSingleDocument(
        @Field("document_id") documentId: String,
        @Field("fields") fields: String,  // JSON string
        @Field("use_ai") useAI: Boolean = true
    ): Response<ExtractionResult>

    /**
     * Obtiene el estado de un lote
     */
    @GET("extraction/batch/{batchId}")
    suspend fun getBatchStatus(
        @Path("batchId") batchId: String
    ): Response<ExtractionBatch>

    // ============= EXPORTACIÓN =============

    /**
     * Exporta resultados a Excel
     */
    @FormUrlEncoded
    @POST("export/excel")
    @Streaming
    suspend fun exportToExcel(
        @Field("batch_id") batchId: String,
        @Field("template_config") templateConfig: String  // JSON string
    ): Response<ResponseBody>

    /**
     * Descarga un archivo generado
     */
    @GET("download/{filename}")
    @Streaming
    suspend fun downloadFile(
        @Path("filename") filename: String
    ): Response<ResponseBody>

    // ============= UTILIDADES =============

    /**
     * Verifica el estado del servidor
     */
    @GET("health")
    suspend fun healthCheck(): Response<HealthResponse>

    /**
     * Obtiene tipos de campo disponibles
     */
    @GET("field-types")
    suspend fun getFieldTypes(): Response<List<FieldTypeOption>>
}

/**
 * Solicitud de extracción
 */
data class ExtractionRequest(
    @com.google.gson.annotations.SerializedName("template_config")
    val templateConfig: TemplateConfig,
    @com.google.gson.annotations.SerializedName("document_ids")
    val documentIds: List<String>,
    @com.google.gson.annotations.SerializedName("use_ai")
    val useAI: Boolean = true
)

/**
 * Opción de tipo de campo
 */
data class FieldTypeOption(
    val value: String,
    val label: String
)
