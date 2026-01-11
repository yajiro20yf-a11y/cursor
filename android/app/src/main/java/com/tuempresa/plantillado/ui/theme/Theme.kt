package com.tuempresa.plantillado.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF1E88E5),
    secondary = Color(0xFF1565C0),
    tertiary = Color(0xFF26A69A),
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF90CAF9),
    secondary = Color(0xFF64B5F6),
    tertiary = Color(0xFF80CBC4),
)

@Composable
fun PlantilladoTheme(content: @Composable () -> Unit) {
    // Si quieres, después lo conectamos a isSystemInDarkTheme().
    MaterialTheme(
        colorScheme = LightColors,
        content = content,
    )
}

