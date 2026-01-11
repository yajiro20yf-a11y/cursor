package com.dataextractor.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.runtime.*
import androidx.compose.material3.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.dataextractor.ai.data.models.ExtractionResult
import com.dataextractor.ai.data.models.ProcessingStatus
import com.dataextractor.ai.ui.MainUiState
import com.dataextractor.ai.ui.components.*

/**
 * Pantalla de resultados
 */
@Composable
fun ResultsScreen(
    uiState: MainUiState,
    onExportExcel: () -> Unit,
    onNewProcess: () -> Unit
) {
    val batch = uiState.extractionBatch
    
    if (batch == null) {
        // No hay resultados
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Error,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(64.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "No hay resultados disponibles",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(24.dp))
            PrimaryButton(
                text = "Nuevo proceso",
                onClick = onNewProcess,
                icon = Icons.Default.Refresh
            )
        }
        return
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header con acciones
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            Column {
                Text(
                    text = "Resultados de Extracción",
                    style = MaterialTheme.typography.headlineSmall
                )
                Text(
                    text = "Revisa los datos y descarga el Excel",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Button(
                onClick = onExportExcel,
                enabled = !uiState.isLoading
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colorScheme.onPrimary,
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(imageVector = Icons.Default.Download, contentDescription = null)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text("Descargar")
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Estadísticas
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                value = "${batch.totalDocuments}",
                label = "Total",
                backgroundColor = Color(0xFFEFF6FF),
                textColor = Color(0xFF2563EB),
                modifier = Modifier.weight(1f)
            )
            StatCard(
                value = "${batch.successfulExtractions}",
                label = "Exitosos",
                backgroundColor = Color(0xFFF0FDF4),
                textColor = Color(0xFF16A34A),
                modifier = Modifier.weight(1f)
            )
            StatCard(
                value = "${batch.totalDocuments - batch.successfulExtractions}",
                label = "Errores",
                backgroundColor = Color(0xFFFEF2F2),
                textColor = Color(0xFFDC2626),
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Lista de resultados
        Text(
            text = "Detalle por documento",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(batch.results) { result ->
                ResultItem(
                    result = result,
                    fields = uiState.templateConfig?.fields ?: emptyList()
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Archivo exportado
        uiState.exportedFile?.let { file ->
            Surface(
                color = Color(0xFFF0FDF4),
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
                        imageVector = Icons.Default.InsertDriveFile,
                        contentDescription = null,
                        tint = Color(0xFF16A34A),
                        modifier = Modifier.size(40.dp)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Archivo guardado",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF16A34A)
                        )
                        Text(
                            text = file.name,
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFF16A34A)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // Botón nuevo proceso
        SecondaryButton(
            text = "Nuevo proceso",
            onClick = onNewProcess,
            icon = Icons.Default.Refresh,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/**
 * Item de resultado de extracción
 */
@Composable
fun ResultItem(
    result: ExtractionResult,
    fields: List<com.dataextractor.ai.data.models.TemplateField>
) {
    var expanded by remember { mutableStateOf(false) }
    
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = MaterialTheme.shapes.medium,
        border = ButtonDefaults.outlinedButtonBorder,
        onClick = { expanded = !expanded }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = when (result.status) {
                            ProcessingStatus.COMPLETED -> Icons.Default.CheckCircle
                            ProcessingStatus.ERROR -> Icons.Default.Error
                            else -> Icons.Default.Schedule
                        },
                        contentDescription = null,
                        tint = when (result.status) {
                            ProcessingStatus.COMPLETED -> Color(0xFF16A34A)
                            ProcessingStatus.ERROR -> Color(0xFFDC2626)
                            else -> MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    )
                    Column {
                        Text(
                            text = result.documentName,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "Procesado en ${result.processingTimeMs}ms",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    ConfidenceBadge(confidence = result.confidenceScore)
                    Icon(
                        imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            // Contenido expandido
            if (expanded) {
                Spacer(modifier = Modifier.height(16.dp))
                HorizontalDivider()
                Spacer(modifier = Modifier.height(16.dp))
                
                if (result.status == ProcessingStatus.ERROR) {
                    Surface(
                        color = Color(0xFFFEF2F2),
                        shape = MaterialTheme.shapes.small
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Error,
                                contentDescription = null,
                                tint = Color(0xFFDC2626)
                            )
                            Text(
                                text = result.errorMessage ?: "Error desconocido",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color(0xFFDC2626)
                            )
                        }
                    }
                } else {
                    // Campos extraídos
                    fields.forEach { field ->
                        val mapping = result.fields[field.id]
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = field.name,
                                    style = MaterialTheme.typography.labelMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Text(
                                    text = mapping?.extractedValue?.toString() ?: "No encontrado",
                                    style = MaterialTheme.typography.bodyMedium,
                                    fontWeight = FontWeight.Medium,
                                    color = if (mapping?.extractedValue != null)
                                        MaterialTheme.colorScheme.onSurface
                                    else
                                        MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            mapping?.let {
                                ConfidenceBadge(confidence = it.confidence)
                            }
                        }
                        if (field != fields.last()) {
                            HorizontalDivider(
                                modifier = Modifier.padding(vertical = 8.dp),
                                color = MaterialTheme.colorScheme.outlineVariant
                            )
                        }
                    }
                }
            }
        }
    }
}
