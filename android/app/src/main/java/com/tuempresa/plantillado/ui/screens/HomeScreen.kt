package com.tuempresa.plantillado.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HomeScreen(
    onGoTemplate: () -> Unit,
    onGoNewBatch: () -> Unit,
    onGoHistory: () -> Unit,
    onGoSettings: () -> Unit,
) {
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterVertically),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "Plantillado",
                style = MaterialTheme.typography.headlineMedium,
            )

            Button(onClick = onGoTemplate) { Text("Cargar plantilla (Excel)") }
            Button(onClick = onGoNewBatch) { Text("Nueva captura en masa") }
            Button(onClick = onGoHistory) { Text("Historial") }
            Button(onClick = onGoSettings) { Text("Ajustes") }
        }
    }
}

