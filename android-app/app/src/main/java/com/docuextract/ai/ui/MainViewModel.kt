package com.docuextract.ai.ui

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.docuextract.ai.data.models.*
import com.docuextract.ai.data.repository.DataExtractorRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

/**
 * Estado de la UI
 */
data class MainUiState(
    // Paso actual del wizard (0-4)
    val currentStep: Int = 0,
    
    // Plantilla
    val templateAnalysis: TemplateAnalysis? = null,
    val templateConfig: TemplateConfig? = null,
    val templateFields: List<TemplateField> = emptyList(),
    
    // Documentos
    val selectedDocumentUris: List<Uri> = emptyList(),
    val uploadedDocuments: List<DocumentUpload> = emptyList(),
    
    // Resultados
    val extractionBatch: ExtractionBatch? = null,
    val exportedFile: File? = null,
    
    // Estado de UI
    val isLoading: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
    
    // Opciones
    val useAI: Boolean = true,
    val selectedSheetName: String? = null,
    val startRow: Int = 2,
    val templateName: String = ""
)

/**
 * ViewModel principal de la aplicación
 */
@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: DataExtractorRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    // ============= NAVEGACIÓN =============

    fun nextStep() {
        _uiState.update { it.copy(currentStep = minOf(it.currentStep + 1, 4)) }
    }

    fun previousStep() {
        _uiState.update { it.copy(currentStep = maxOf(it.currentStep - 1, 0)) }
    }

    fun goToStep(step: Int) {
        _uiState.update { it.copy(currentStep = step.coerceIn(0, 4)) }
    }

    // ============= PLANTILLA =============

    fun uploadTemplate(uri: Uri) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            repository.uploadTemplate(uri).fold(
                onSuccess = { analysis ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            templateAnalysis = analysis,
                            templateFields = analysis.detectedFields,
                            templateName = analysis.templateId,
                            selectedSheetName = analysis.sheetNames?.firstOrNull()
                        )
                    }
                    nextStep()
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    fun updateTemplateName(name: String) {
        _uiState.update { it.copy(templateName = name) }
    }

    fun updateSelectedSheet(sheetName: String) {
        _uiState.update { it.copy(selectedSheetName = sheetName) }
    }

    fun updateStartRow(row: Int) {
        _uiState.update { it.copy(startRow = row) }
    }

    // ============= CAMPOS =============

    fun updateField(index: Int, field: TemplateField) {
        val updatedFields = _uiState.value.templateFields.toMutableList()
        if (index in updatedFields.indices) {
            updatedFields[index] = field
            _uiState.update { it.copy(templateFields = updatedFields) }
        }
    }

    fun addField() {
        val newField = TemplateField(
            id = "field_${System.currentTimeMillis()}",
            name = "Nuevo Campo",
            fieldType = FieldType.TEXT,
            required = false
        )
        _uiState.update { it.copy(templateFields = it.templateFields + newField) }
    }

    fun removeField(index: Int) {
        val updatedFields = _uiState.value.templateFields.toMutableList()
        if (index in updatedFields.indices) {
            updatedFields.removeAt(index)
            _uiState.update { it.copy(templateFields = updatedFields) }
        }
    }

    fun configureTemplate() {
        viewModelScope.launch {
            val state = _uiState.value
            val analysis = state.templateAnalysis ?: return@launch
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            repository.configureTemplate(
                templateId = analysis.templateId,
                templateName = state.templateName,
                fields = state.templateFields,
                sheetName = state.selectedSheetName,
                startRow = state.startRow
            ).fold(
                onSuccess = { config ->
                    _uiState.update {
                        it.copy(isLoading = false, templateConfig = config)
                    }
                    nextStep()
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    // ============= DOCUMENTOS =============

    fun addDocumentUris(uris: List<Uri>) {
        _uiState.update {
            it.copy(selectedDocumentUris = it.selectedDocumentUris + uris)
        }
    }

    fun removeDocumentUri(index: Int) {
        val updatedUris = _uiState.value.selectedDocumentUris.toMutableList()
        if (index in updatedUris.indices) {
            updatedUris.removeAt(index)
            _uiState.update { it.copy(selectedDocumentUris = updatedUris) }
        }
    }

    fun uploadDocuments() {
        viewModelScope.launch {
            val uris = _uiState.value.selectedDocumentUris
            if (uris.isEmpty()) {
                _uiState.update { it.copy(error = "Selecciona al menos un documento") }
                return@launch
            }
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            repository.uploadDocuments(uris).fold(
                onSuccess = { documents ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            uploadedDocuments = it.uploadedDocuments + documents,
                            selectedDocumentUris = emptyList(),
                            successMessage = "${documents.size} documento(s) subido(s)"
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    fun removeUploadedDocument(documentId: String) {
        viewModelScope.launch {
            repository.deleteDocument(documentId).fold(
                onSuccess = {
                    _uiState.update {
                        it.copy(
                            uploadedDocuments = it.uploadedDocuments.filter { d -> d.id != documentId }
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update { it.copy(error = error.message) }
                }
            )
        }
    }

    // ============= EXTRACCIÓN =============

    fun setUseAI(useAI: Boolean) {
        _uiState.update { it.copy(useAI = useAI) }
    }

    fun startProcessing() {
        viewModelScope.launch {
            val state = _uiState.value
            val config = state.templateConfig ?: return@launch
            val documentIds = state.uploadedDocuments.map { it.id }
            
            if (documentIds.isEmpty()) {
                _uiState.update { it.copy(error = "No hay documentos para procesar") }
                return@launch
            }
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            repository.processExtraction(config, documentIds, state.useAI).fold(
                onSuccess = { batch ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            extractionBatch = batch,
                            successMessage = "Procesados ${batch.successfulExtractions} de ${batch.totalDocuments} documentos"
                        )
                    }
                    nextStep()
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    // ============= EXPORTACIÓN =============

    fun exportToExcel() {
        viewModelScope.launch {
            val state = _uiState.value
            val batch = state.extractionBatch ?: return@launch
            val config = state.templateConfig ?: return@launch
            
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            repository.exportToExcel(batch.id, config).fold(
                onSuccess = { file ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            exportedFile = file,
                            successMessage = "Archivo guardado: ${file.name}"
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    // ============= UTILIDADES =============

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    fun clearSuccessMessage() {
        _uiState.update { it.copy(successMessage = null) }
    }

    fun resetAll() {
        _uiState.value = MainUiState()
    }

    fun checkServerHealth() {
        viewModelScope.launch {
            repository.checkHealth().fold(
                onSuccess = { /* Servidor disponible */ },
                onFailure = { error ->
                    _uiState.update { it.copy(error = "No se puede conectar al servidor: ${error.message}") }
                }
            )
        }
    }
}
