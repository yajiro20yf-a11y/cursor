# DocuFill AI - Extractor y Rellenador Inteligente de Documentos

## Descripción
Esta aplicación permite automatizar el llenado de plantillas (Excel/Word) extrayendo datos de múltiples fuentes (PDFs escaneados, imágenes) utilizando Inteligencia Artificial, manteniendo el formato original de la plantilla.

## Arquitectura del Sistema con Soporte Móvil (Android)

El proyecto está diseñado para funcionar como una aplicación híbrida Cliente-Servidor, optimizada para su despliegue como APK en Android.

### 1. Aplicación Móvil (Cliente - Android Studio)
- **Tecnología:** React Native (Compatible con Android Studio para generación de APK).
- **Función Principal:** Escáner Masivo y Selección de Plantillas.
- **Capacidades:**
  - Uso de cámara nativa para tomar fotos en ráfaga (Batch Scanning) de documentos.
  - Interfaz táctil para seleccionar áreas de la plantilla.
  - Comunicación directa con el Backend para procesamiento.
  - **Depuración:** Estructura lista para abrir la carpeta `/mobile/android` directamente en Android Studio y depurar en dispositivo físico o emulador.

### 2. Backend (API & Procesamiento)
- **Tecnología:** Python (FastAPI).
- **Rol:** "Cerebro" de la operación (se ejecuta en servidor o PC local).
- **Módulos:**
  - `DocumentParser`: Lee archivos Word (.docx) y Excel (.xlsx) preservando estilos.
  - `OCRService`: Convierte imágenes escaneadas a texto plano.
  - `AIExtractor`: Usa LLMs para entender el texto desordenado.
  - `ReportGenerator`: Inyecta datos en la plantilla original.

## Flujo de Trabajo Móvil

1. **Configuración de Plantilla:**
   - El usuario sube `Plantilla.xlsx` desde el móvil o selecciona una existente.
   - En la pantalla del celular, toca las celdas donde quiere que vayan los datos.
   
2. **Ingesta de Datos (Escaneo Masivo):**
   - El usuario activa la cámara desde la App.
   - Toma fotos consecutivas de varios documentos.
   - La App envía las imágenes al Backend.
   
3. **Procesamiento y Resultados:**
   - El servidor procesa y devuelve los archivos Excel generados.
   - El usuario descarga los archivos finales en su dispositivo Android.

## Estructura de Carpetas

- `/backend`: Lógica del servidor Python (FastAPI).
- `/mobile`: Código fuente de la App (React Native). Contiene la subcarpeta `/android` generable para Android Studio.
- `/documents`: Almacenamiento temporal.

## Notas para Desarrollo en Android Studio
Para generar el APK o depurar:
1. Asegurarse de que el Backend esté corriendo (IP local).
2. Abrir la carpeta `mobile` en terminal y ejecutar la pre-construcción.
3. Abrir la carpeta `mobile/android` en Android Studio.
4. Conectar dispositivo USB y dar clic en "Run".
