package com.dataextractor.ai

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Aplicación principal de DataExtractor AI
 * Inicializa Hilt para inyección de dependencias
 */
@HiltAndroidApp
class DataExtractorApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // Inicializaciones adicionales si es necesario
    }
}
