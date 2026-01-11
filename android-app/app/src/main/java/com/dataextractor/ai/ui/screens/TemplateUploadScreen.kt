package com.dataextractor.ai.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.dataextractor.ai.ui.MainUiState
import com.dataextractor.ai.ui.components.*

/**
 * Pantalla de subida de plantilla
 */
@Composable
fun TemplateUploadScreen(
    uiState: MainUiState,
    onUploadTemplate: (Uri) -> Unit
) {
    var selectedUri by remember { mutableStateOf<Uri?>(null) }
    
    // Selector de archivos
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri ->
        uri?.let { selectedUri = it }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Título
        Text(
            text = "Subir Plantilla",
            style = MaterialTheme.typography.headlineSmall
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Sube tu plantilla Excel o Word. El sistema analizará su estructura para detectar los campos.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Tarjetas informativas
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            InfoCard(
                title = "Excel (.xlsx)",
                description = "Plantillas con columnas para cada campo",
                icon = Icons.Default.TableChart,
                iconColor = Color(0xFF2563EB),
                backgroundColor = Color(0xFFEFF6FF),
                modifier = Modifier.weight(1f)
            )
            
            InfoCard(
                title = "Word (.docx)",
                description = "Plantillas con marcadores {{campo}}",
                icon = Icons.Default.Description,
                iconColor = Color(0xFF7C3AED),
                backgroundColor = Color(0xFFF5F3FF),
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Zona de selección
        DropZone(
            title = "Seleccionar plantilla",
            description = "Toca para elegir un archivo Excel o Word",
            onClick = {
                filePickerLauncher.launch(
                    arrayOf(
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                )
            },
            isActive = selectedUri != null
        )
        
        // Archivo seleccionado
        selectedUri?.let { uri ->
            Spacer(modifier = Modifier.height(16.dp))
            
            FileListItem(
                fileName = uri.lastPathSegment ?: "Archivo seleccionado",
                fileSize = "Listo para subir",
                icon = Icons.Default.InsertDriveFile,
                iconColor = MaterialTheme.colorScheme.primary,
                onRemove = { selectedUri = null }
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Consejo
        Surface(
            color = Color(0xFFFFFBEB),
            shape = MaterialTheme.shapes.medium
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Lightbulb,
                    contentDescription = null,
                    tint = Color(0xFFD97706)
                )
                Column {
                    Text(
                        text = "Consejo",
                        style = MaterialTheme.typography.titleSmall,
                        color = Color(0xFF92400E)
                    )
                    Text(
                        text = "Para Excel: la primera fila debe contener los nombres de las columnas. Para Word: usa marcadores como {{nombre}}, {{fecha}}.",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF92400E)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        Spacer(modifier = Modifier.height(16.dp))
        
        // Botón continuar
        PrimaryButton(
            text = if (uiState.isLoading) "Analizando..." else "Continuar",
            onClick = { selectedUri?.let { onUploadTemplate(it) } },
            enabled = selectedUri != null,
            isLoading = uiState.isLoading,
            icon = Icons.Default.ArrowForward,
            modifier = Modifier.fillMaxWidth()
        )
    }
}
