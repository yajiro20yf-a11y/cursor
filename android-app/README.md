# 📱 DataExtractor AI - Android App

Aplicación móvil nativa para Android que permite extraer datos de documentos escaneados y fotos utilizando Inteligencia Artificial.

## 📋 Requisitos

- **Android Studio** Hedgehog (2023.1.1) o superior
- **JDK 17** o superior
- **Android SDK 34** (Android 14)
- **Min SDK 26** (Android 8.0)

## 🚀 Configuración del Proyecto

### 1. Abrir en Android Studio

1. Abre Android Studio
2. Selecciona **File > Open**
3. Navega a la carpeta `android-app`
4. Espera a que Gradle sincronice el proyecto

### 2. Configurar el Backend

La app se conecta a un servidor backend. Por defecto usa `http://10.0.2.2:8000/api/v1/` que es la dirección del host desde el emulador.

Para cambiar la URL, edita `app/build.gradle.kts`:

```kotlin
buildConfigField("String", "API_BASE_URL", "\"http://tu-servidor.com/api/v1/\"")
```

### 3. Ejecutar la Aplicación

1. Conecta un dispositivo Android o inicia un emulador
2. Haz clic en el botón **Run** (▶️)
3. Espera a que la app se compile e instale

## 📱 Funcionalidades

### Paso 1: Subir Plantilla
- Selecciona una plantilla Excel (.xlsx) o Word (.docx)
- La app analiza la estructura y detecta campos

### Paso 2: Configurar Campos
- Edita los campos detectados
- Define el tipo de dato (texto, número, fecha, etc.)
- Agrega descripciones para ayudar a la IA

### Paso 3: Subir Documentos
- Selecciona fotos desde la galería
- Soporta JPG, PNG, PDF
- Procesa múltiples documentos a la vez

### Paso 4: Procesar
- Activa/desactiva extracción con IA
- Visualiza el progreso en tiempo real

### Paso 5: Resultados
- Revisa los datos extraídos por documento
- Verifica niveles de confianza
- Descarga el archivo Excel

## 🏗️ Arquitectura

```
app/
├── data/
│   ├── api/
│   │   ├── ApiService.kt       # Interfaz Retrofit
│   │   └── NetworkModule.kt    # Módulo Hilt para red
│   ├── models/
│   │   └── Models.kt           # Modelos de datos
│   └── repository/
│       └── DataExtractorRepository.kt
├── ui/
│   ├── components/             # Componentes reutilizables
│   │   ├── CommonComponents.kt
│   │   ├── StepIndicator.kt
│   │   └── TopBar.kt
│   ├── navigation/
│   │   └── NavHost.kt          # Navegación
│   ├── screens/                # Pantallas del wizard
│   │   ├── TemplateUploadScreen.kt
│   │   ├── FieldConfigurationScreen.kt
│   │   ├── DocumentUploadScreen.kt
│   │   ├── ProcessingScreen.kt
│   │   └── ResultsScreen.kt
│   ├── theme/
│   │   ├── Theme.kt
│   │   └── Type.kt
│   └── MainViewModel.kt        # ViewModel principal
├── DataExtractorApp.kt         # Application class
└── MainActivity.kt             # Activity principal
```

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Kotlin | 1.9.21 | Lenguaje principal |
| Jetpack Compose | 1.5.6 | UI declarativa |
| Material 3 | Latest | Design system |
| Hilt | 2.48 | Inyección de dependencias |
| Retrofit | 2.9.0 | Cliente HTTP |
| Coil | 2.5.0 | Carga de imágenes |
| CameraX | 1.3.1 | Acceso a cámara |
| ML Kit | 16.0.0 | OCR local (opcional) |

## ⚙️ Configuración Adicional

### Permisos Requeridos

La app solicita los siguientes permisos:
- **INTERNET**: Comunicación con el servidor
- **CAMERA**: Tomar fotos de documentos
- **READ_MEDIA_IMAGES**: Acceder a la galería

### ProGuard

Las reglas de ProGuard están configuradas en `app/proguard-rules.pro` para:
- Mantener modelos de datos
- Configuración de Retrofit/Gson
- Hilt y Coroutines

## 🔧 Solución de Problemas

### Error de conexión al servidor

1. Verifica que el backend esté corriendo
2. Si usas emulador, la IP del host es `10.0.2.2`
3. Si usas dispositivo físico, usa la IP de tu computadora
4. Asegúrate de habilitar `usesCleartextTraffic` para HTTP

### Error al compilar

1. Sincroniza Gradle: **File > Sync Project with Gradle Files**
2. Limpia el proyecto: **Build > Clean Project**
3. Invalida caché: **File > Invalidate Caches**

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.
