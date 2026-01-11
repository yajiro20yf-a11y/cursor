package com.dataextractor.ai.ui.navigation

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import com.dataextractor.ai.ui.MainViewModel
import com.dataextractor.ai.ui.screens.*
import com.dataextractor.ai.ui.components.StepIndicator
import com.dataextractor.ai.ui.components.TopBar

/**
 * Navegación principal de la aplicación con wizard de pasos
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DataExtractorNavHost(
    viewModel: MainViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    // Snackbar para mensajes
    val snackbarHostState = remember { SnackbarHostState() }
    
    // Mostrar error
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(
                message = error,
                duration = SnackbarDuration.Short
            )
            viewModel.clearError()
        }
    }
    
    // Mostrar mensaje de éxito
    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                duration = SnackbarDuration.Short
            )
            viewModel.clearSuccessMessage()
        }
    }
    
    Scaffold(
        topBar = {
            TopBar(
                onResetClick = { viewModel.resetAll() }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Indicador de pasos
            StepIndicator(
                currentStep = uiState.currentStep,
                totalSteps = 5,
                stepNames = listOf("Plantilla", "Campos", "Documentos", "Procesar", "Resultados")
            )
            
            // Contenido según el paso actual
            when (uiState.currentStep) {
                0 -> TemplateUploadScreen(
                    uiState = uiState,
                    onUploadTemplate = { viewModel.uploadTemplate(it) }
                )
                
                1 -> FieldConfigurationScreen(
                    uiState = uiState,
                    onUpdateTemplateName = { viewModel.updateTemplateName(it) },
                    onUpdateSelectedSheet = { viewModel.updateSelectedSheet(it) },
                    onUpdateStartRow = { viewModel.updateStartRow(it) },
                    onUpdateField = { index, field -> viewModel.updateField(index, field) },
                    onAddField = { viewModel.addField() },
                    onRemoveField = { viewModel.removeField(it) },
                    onContinue = { viewModel.configureTemplate() },
                    onBack = { viewModel.previousStep() }
                )
                
                2 -> DocumentUploadScreen(
                    uiState = uiState,
                    onAddDocuments = { viewModel.addDocumentUris(it) },
                    onRemoveSelectedDocument = { viewModel.removeDocumentUri(it) },
                    onUploadDocuments = { viewModel.uploadDocuments() },
                    onRemoveUploadedDocument = { viewModel.removeUploadedDocument(it) },
                    onContinue = { viewModel.nextStep() },
                    onBack = { viewModel.previousStep() }
                )
                
                3 -> ProcessingScreen(
                    uiState = uiState,
                    onSetUseAI = { viewModel.setUseAI(it) },
                    onStartProcessing = { viewModel.startProcessing() },
                    onBack = { viewModel.previousStep() }
                )
                
                4 -> ResultsScreen(
                    uiState = uiState,
                    onExportExcel = { viewModel.exportToExcel() },
                    onNewProcess = { viewModel.resetAll() }
                )
            }
        }
    }
}
