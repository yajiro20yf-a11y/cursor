package com.dataextractor.ai.data.repository

import android.content.Context
import android.net.Uri
import com.dataextractor.ai.data.api.ApiService
import com.dataextractor.ai.data.api.ExtractionRequest
import com.dataextractor.ai.data.models.*
import com.google.gson.Gson
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.io.FileOutputStream
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repositorio principal para operaciones de extracción de datos
 */
@Singleton
class DataExtractorRepository @Inject constructor(
    private val apiService: ApiService,
    @ApplicationContext private val context: Context
) {
    private val gson = Gson()

    // ============= PLANTILLAS =============

    /**
     * Sube y analiza una plantilla
     */
    suspend fun uploadTemplate(uri: Uri, templateName: String? = null): Result<TemplateAnalysis> {
        return withContext(Dispatchers.IO) {
            try {
                val file = uriToFile(uri)
                val requestFile = file.asRequestBody(
                    getMimeType(uri).toMediaTypeOrNull()
                )
                val filePart = MultipartBody.Part.createFormData(
                    "file",
                    file.name,
                    requestFile
                )
                
                val namePart = templateName?.toRequestBody("text/plain".toMediaTypeOrNull())
                
                val response = apiService.uploadTemplate(filePart, namePart)
                
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(response.errorBody()?.string() ?: "Error al subir plantilla"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    /**
     * Configura los campos de una plantilla
     */
    suspend fun configureTemplate(
        templateId: String,
        templateName: String,
        fields: List<TemplateField>,
        sheetName: String? = null,
        startRow: Int = 2
    ): Result<TemplateConfig> {
        return withContext(Dispatchers.IO) {
            try {
                val fieldsJson = gson.toJson(fields)
                val response = apiService.configureTemplate(
                    templateId, templateName, fieldsJson, sheetName, startRow
                )
                
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(response.errorBody()?.string() ?: "Error al configurar"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    // ============= DOCUMENTOS =============

    /**
     * Sube múltiples documentos
     */
    suspend fun uploadDocuments(uris: List<Uri>): Result<List<DocumentUpload>> {
        return withContext(Dispatchers.IO) {
            try {
                val parts = uris.map { uri ->
                    val file = uriToFile(uri)
                    val requestFile = file.asRequestBody(
                        getMimeType(uri).toMediaTypeOrNull()
                    )
                    MultipartBody.Part.createFormData("files", file.name, requestFile)
                }
                
                val response = apiService.uploadDocuments(parts)
                
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(response.errorBody()?.string() ?: "Error al subir documentos"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    /**
     * Elimina un documento
     */
    suspend fun deleteDocument(documentId: String): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.deleteDocument(documentId)
                if (response.isSuccessful) {
                    Result.success(Unit)
                } else {
                    Result.failure(Exception("Error al eliminar documento"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    // ============= EXTRACCIÓN =============

    /**
     * Procesa un lote de documentos
     */
    suspend fun processExtraction(
        templateConfig: TemplateConfig,
        documentIds: List<String>,
        useAI: Boolean = true
    ): Result<ExtractionBatch> {
        return withContext(Dispatchers.IO) {
            try {
                val request = ExtractionRequest(templateConfig, documentIds, useAI)
                val response = apiService.processExtraction(request)
                
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception(response.errorBody()?.string() ?: "Error en procesamiento"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    /**
     * Obtiene el estado de un lote
     */
    suspend fun getBatchStatus(batchId: String): Result<ExtractionBatch> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getBatchStatus(batchId)
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception("Error al obtener estado"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    // ============= EXPORTACIÓN =============

    /**
     * Exporta resultados a Excel y guarda en descargas
     */
    suspend fun exportToExcel(
        batchId: String,
        templateConfig: TemplateConfig
    ): Result<File> {
        return withContext(Dispatchers.IO) {
            try {
                val configJson = gson.toJson(templateConfig)
                val response = apiService.exportToExcel(batchId, configJson)
                
                if (response.isSuccessful) {
                    val body = response.body()!!
                    val fileName = "${templateConfig.name}_datos_${System.currentTimeMillis()}.xlsx"
                    val file = File(context.getExternalFilesDir(null), fileName)
                    
                    FileOutputStream(file).use { output ->
                        body.byteStream().use { input ->
                            input.copyTo(output)
                        }
                    }
                    
                    Result.success(file)
                } else {
                    Result.failure(Exception("Error al exportar"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    // ============= UTILIDADES =============

    /**
     * Verifica la conexión con el servidor
     */
    suspend fun checkHealth(): Result<HealthResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.healthCheck()
                if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(Exception("Servidor no disponible"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    /**
     * Convierte Uri a File temporal
     */
    private fun uriToFile(uri: Uri): File {
        val inputStream = context.contentResolver.openInputStream(uri)
        val fileName = getFileName(uri) ?: "temp_${System.currentTimeMillis()}"
        val tempFile = File(context.cacheDir, fileName)
        
        inputStream?.use { input ->
            FileOutputStream(tempFile).use { output ->
                input.copyTo(output)
            }
        }
        
        return tempFile
    }

    /**
     * Obtiene el nombre del archivo desde Uri
     */
    private fun getFileName(uri: Uri): String? {
        val cursor = context.contentResolver.query(uri, null, null, null, null)
        return cursor?.use {
            val nameIndex = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
            it.moveToFirst()
            it.getString(nameIndex)
        }
    }

    /**
     * Obtiene el tipo MIME desde Uri
     */
    private fun getMimeType(uri: Uri): String {
        return context.contentResolver.getType(uri) ?: "application/octet-stream"
    }
}
