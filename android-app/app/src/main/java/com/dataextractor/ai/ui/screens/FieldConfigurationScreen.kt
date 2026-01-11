package com.dataextractor.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.dataextractor.ai.data.models.FieldType
import com.dataextractor.ai.data.models.TemplateField
import com.dataextractor.ai.ui.MainUiState
import com.dataextractor.ai.ui.components.*

/**
 * Pantalla de configuración de campos
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FieldConfigurationScreen(
    uiState: MainUiState,
    onUpdateTemplateName: (String) -> Unit,
    onUpdateSelectedSheet: (String) -> Unit,
    onUpdateStartRow: (Int) -> Unit,
    onUpdateField: (Int, TemplateField) -> Unit,
    onAddField: () -> Unit,
    onRemoveField: (Int) -> Unit,
    onContinue: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Título
        Text(
            text = "Configurar Campos",
            style = MaterialTheme.typography.headlineSmall
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Selecciona y configura los campos que quieres extraer de los documentos.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Configuración general
        Surface(
            color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
            shape = MaterialTheme.shapes.medium
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                // Nombre de plantilla
                OutlinedTextField(
                    value = uiState.templateName,
                    onValueChange = onUpdateTemplateName,
                    label = { Text("Nombre de plantilla") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    // Selector de hoja (si aplica)
                    uiState.templateAnalysis?.sheetNames?.let { sheets ->
                        if (sheets.size > 1) {
                            var expanded by remember { mutableStateOf(false) }
                            
                            ExposedDropdownMenuBox(
                                expanded = expanded,
                                onExpandedChange = { expanded = it },
                                modifier = Modifier.weight(1f)
                            ) {
                                OutlinedTextField(
                                    value = uiState.selectedSheetName ?: "",
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("Hoja") },
                                    trailingIcon = {
                                        ExposedDropdownMenuDefaults.TrailingIcon(expanded)
                                    },
                                    modifier = Modifier.menuAnchor()
                                )
                                ExposedDropdownMenu(
                                    expanded = expanded,
                                    onDismissRequest = { expanded = false }
                                ) {
                                    sheets.forEach { sheet ->
                                        DropdownMenuItem(
                                            text = { Text(sheet) },
                                            onClick = {
                                                onUpdateSelectedSheet(sheet)
                                                expanded = false
                                            }
                                        )
                                    }
                                }
                            }
                        }
                    }
                    
                    // Fila inicial
                    OutlinedTextField(
                        value = uiState.startRow.toString(),
                        onValueChange = { it.toIntOrNull()?.let(onUpdateStartRow) },
                        label = { Text("Fila inicial") },
                        modifier = Modifier.width(100.dp),
                        singleLine = true
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Header de campos
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Campos (${uiState.templateFields.size})",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }
            
            TextButton(onClick = onAddField) {
                Icon(imageVector = Icons.Default.Add, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Agregar")
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Lista de campos
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            itemsIndexed(uiState.templateFields) { index, field ->
                FieldConfigItem(
                    field = field,
                    onUpdate = { onUpdateField(index, it) },
                    onRemove = { onRemoveField(index) }
                )
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
                text = if (uiState.isLoading) "Guardando..." else "Continuar",
                onClick = onContinue,
                enabled = uiState.templateFields.isNotEmpty(),
                isLoading = uiState.isLoading,
                icon = Icons.Default.ArrowForward,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

/**
 * Item de configuración de campo
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FieldConfigItem(
    field: TemplateField,
    onUpdate: (TemplateField) -> Unit,
    onRemove: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = MaterialTheme.shapes.medium,
        border = ButtonDefaults.outlinedButtonBorder
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.DragIndicator,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.outline
                )
                
                // Nombre del campo
                OutlinedTextField(
                    value = field.name,
                    onValueChange = { onUpdate(field.copy(name = it)) },
                    label = { Text("Nombre") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                
                // Tipo de campo
                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { expanded = it },
                    modifier = Modifier.width(130.dp)
                ) {
                    OutlinedTextField(
                        value = field.fieldType.name.lowercase().replaceFirstChar { it.uppercase() },
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Tipo") },
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
                        modifier = Modifier.menuAnchor(),
                        singleLine = true
                    )
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        FieldType.values().forEach { type ->
                            DropdownMenuItem(
                                text = { Text(type.name.lowercase().replaceFirstChar { it.uppercase() }) },
                                onClick = {
                                    onUpdate(field.copy(fieldType = type))
                                    expanded = false
                                }
                            )
                        }
                    }
                }
                
                // Botón eliminar
                IconButton(onClick = onRemove) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Eliminar",
                        tint = MaterialTheme.colorScheme.error
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Descripción
                OutlinedTextField(
                    value = field.description ?: "",
                    onValueChange = { onUpdate(field.copy(description = it.ifEmpty { null })) },
                    label = { Text("Descripción (ayuda a la IA)") },
                    modifier = Modifier.weight(1f),
                    singleLine = true
                )
                
                // Checkbox requerido
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(
                        checked = field.required,
                        onCheckedChange = { onUpdate(field.copy(required = it)) }
                    )
                    Text(
                        text = "Requerido",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}
