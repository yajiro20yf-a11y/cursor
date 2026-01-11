package com.dataextractor.ai.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.dataextractor.ai.data.models.DocumentUpload
import com.dataextractor.ai.ui.MainUiState
import com.dataextractor.ai.ui.components.*

/**
 * Pantalla de subida de documentos
 */
@Composable
fun DocumentUploadScreen(
    uiState: MainUiState,
    onAddDocuments: (List<Uri>) -> Unit,
    onRemoveSelectedDocument: (Int) -> Unit,
    onUploadDocuments: () -> Unit,
    onRemoveUploadedDocument: (String) -> Unit,
    onContinue: () -> Unit,
    onBack: () -> Unit
) {
    // Selector de archivos múltiples
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenMultipleDocuments()
    ) { uris ->
        if (uris.isNotEmpty()) {
            onAddDocuments(uris)
        }
    }
    
    // Selector de cámara
    var photoUri by remember { mutableStateOf<Uri?>(null) }
    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        if (success && photoUri != null) {
            onAddDocuments(listOf(photoUri!!))
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Título
        Text(
            text = "Subir Documentos",
            style = MaterialTheme.typography.headlineSmall
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Sube las fotos o escaneos de los documentos de donde quieres extraer los datos.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Resumen de plantilla
        uiState.templateConfig?.let { config ->
            Surface(
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f),
                shape = MaterialTheme.shapes.medium
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Column {
                        Text(
                            text = "Plantilla: ${config.name}",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "${config.fields.size} campos configurados",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Botones de acción
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Galería
            OutlinedButton(
                onClick = {
                    filePickerLauncher.launch(
                        arrayOf(
                            "image/jpeg",
                            "image/png",
                            "image/tiff",
                            "application/pdf"
                        )
                    )
                },
                modifier = Modifier.weight(1f)
            ) {
                Icon(imageVector = Icons.Default.PhotoLibrary, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Galería")
            }
            
            // Cámara (comentado por ahora - requiere configuración adicional de FileProvider)
            /*
            OutlinedButton(
                onClick = {
                    // Crear URI para foto
                    // cameraLauncher.launch(photoUri)
                },
                modifier = Modifier.weight(1f)
            ) {
                Icon(imageVector = Icons.Default.CameraAlt, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Cámara")
            }
            */
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Lista de documentos
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Documentos seleccionados (aún no subidos)
            if (uiState.selectedDocumentUris.isNotEmpty()) {
                item {
                    Text(
                        text = "Seleccionados (${uiState.selectedDocumentUris.size})",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
                
                itemsIndexed(uiState.selectedDocumentUris) { index, uri ->
                    FileListItem(
                        fileName = uri.lastPathSegment ?: "Documento ${index + 1}",
                        fileSize = "Pendiente de subir",
                        icon = Icons.Default.Image,
                        iconColor = Color(0xFF059669),
                        onRemove = { onRemoveSelectedDocument(index) }
                    )
                }
                
                item {
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(
                        onClick = onUploadDocuments,
                        enabled = !uiState.isLoading,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(imageVector = Icons.Default.CloudUpload, contentDescription = null)
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(if (uiState.isLoading) "Subiendo..." else "Subir ${uiState.selectedDocumentUris.size} archivo(s)")
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
            
            // Documentos ya subidos
            if (uiState.uploadedDocuments.isNotEmpty()) {
                item {
                    Text(
                        text = "Listos para procesar (${uiState.uploadedDocuments.size})",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                }
                
                items(uiState.uploadedDocuments) { doc ->
                    FileListItem(
                        fileName = doc.filename,
                        fileSize = "${doc.fileSize / 1024} KB",
                        icon = if (doc.fileType == "image") Icons.Default.Image else Icons.Default.PictureAsPdf,
                        iconColor = MaterialTheme.colorScheme.primary,
                        onRemove = { onRemoveUploadedDocument(doc.id) }
                    )
                }
            }
            
            // Mensaje si no hay documentos
            if (uiState.selectedDocumentUris.isEmpty() && uiState.uploadedDocuments.isEmpty()) {
                item {
                    Surface(
                        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                        shape = MaterialTheme.shapes.medium,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier.padding(32.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                imageVector = Icons.Default.FolderOpen,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "No hay documentos seleccionados",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Botones de navegación
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            SecondaryButton(
                text = "Anterior",
                onClick = onBack,
                icon = Icons.Default.ArrowBack,
                modifier = Modifier.weight(1f)
            )
            
            PrimaryButton(
                text = "Procesar",
                onClick = onContinue,
                enabled = uiState.uploadedDocuments.isNotEmpty(),
                icon = Icons.Default.ArrowForward,
                modifier = Modifier.weight(1f)
            )
        }
    }
}
