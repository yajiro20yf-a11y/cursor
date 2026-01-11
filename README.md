# 📊 DataExtractor AI

Sistema inteligente para extraer datos de documentos escaneados y fotos, y agregarlos automáticamente a plantillas Excel o Word utilizando Inteligencia Artificial.

![DataExtractor AI](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Características Principales

- **📄 Plantillas Flexibles**: Soporta plantillas Excel (.xlsx) y Word (.docx)
- **📷 Múltiples Formatos**: Procesa imágenes (JPG, PNG, TIFF) y PDFs escaneados
- **🤖 Extracción con IA**: Utiliza GPT-4 Vision para análisis inteligente de documentos
- **🔍 OCR Avanzado**: Reconocimiento óptico de caracteres con Tesseract
- **⚡ Procesamiento por Lotes**: Procesa múltiples documentos simultáneamente
- **🎨 Preserva Formato**: Mantiene el formato original de las plantillas
- **📊 Exportación Excel**: Genera archivos Excel con los datos extraídos

## 🏗️ Arquitectura

```
data-extractor-ai/
├── backend/                    # API Python FastAPI
│   ├── app/
│   │   ├── api/               # Rutas de la API
│   │   ├── models/            # Modelos de datos (Pydantic)
│   │   ├── services/          # Lógica de negocio
│   │   │   ├── ocr_service.py        # Servicio OCR
│   │   │   ├── ai_extractor.py       # Extracción con IA
│   │   │   ├── template_processor.py # Procesador de plantillas
│   │   │   └── document_processor.py # Procesador de documentos
│   │   ├── utils/             # Utilidades
│   │   ├── config.py          # Configuración
│   │   └── main.py            # Punto de entrada
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # Aplicación React
│   ├── src/
│   │   ├── components/        # Componentes reutilizables
│   │   ├── pages/             # Páginas del wizard
│   │   ├── services/          # Cliente API
│   │   ├── hooks/             # Hooks personalizados
│   │   ├── types/             # Tipos TypeScript
│   │   └── styles/            # Estilos CSS
│   ├── package.json
│   └── vite.config.ts
├── templates/                  # Plantillas de usuario
├── uploads/                    # Documentos subidos
└── outputs/                    # Archivos generados
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.9 o superior
- Node.js 18 o superior
- Tesseract OCR instalado en el sistema
- Clave de API de OpenAI (opcional, pero recomendado)

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd data-extractor-ai
```

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración (especialmente OPENAI_API_KEY)
```

### 3. Instalar Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Descargar e instalar desde: https://github.com/UB-Mannheim/tesseract/wiki

### 4. Configurar el Frontend

```bash
cd frontend

# Instalar dependencias
npm install
```

## 🎮 Uso

### Iniciar el Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en: http://localhost:8000
Documentación: http://localhost:8000/docs

### Iniciar el Frontend

```bash
cd frontend
npm run dev
```

La aplicación estará disponible en: http://localhost:3000

## 📖 Flujo de Trabajo

### 1. Subir Plantilla
Sube tu plantilla Excel o Word. El sistema detectará automáticamente los campos disponibles.

### 2. Configurar Campos
Selecciona y configura los campos que deseas extraer de los documentos. Puedes:
- Definir el tipo de dato (texto, número, fecha, email, etc.)
- Agregar descripciones para ayudar a la IA
- Marcar campos como obligatorios

### 3. Subir Documentos
Arrastra tus fotos o escaneos. Soporta:
- Imágenes: JPG, PNG, TIFF, BMP
- PDFs escaneados
- Múltiples archivos a la vez (hasta 50)

### 4. Procesar con IA
La IA analizará cada documento y extraerá los datos según los campos configurados.

### 5. Revisar y Exportar
Revisa los resultados, verifica los niveles de confianza y descarga el archivo Excel final.

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# OpenAI API (para extracción con GPT-4 Vision)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-vision-preview

# Tesseract OCR
TESSERACT_LANG=spa+eng

# Límites
MAX_FILE_SIZE_MB=50
MAX_FILES_PER_BATCH=50

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 🔧 API Endpoints

### Plantillas
- `POST /api/v1/templates/upload` - Subir y analizar plantilla
- `POST /api/v1/templates/configure` - Configurar campos
- `GET /api/v1/templates/{id}/analyze` - Re-analizar plantilla

### Documentos
- `POST /api/v1/documents/upload` - Subir documentos
- `DELETE /api/v1/documents/{id}` - Eliminar documento

### Extracción
- `POST /api/v1/extraction/process` - Procesar lote de documentos
- `POST /api/v1/extraction/single` - Procesar un documento
- `GET /api/v1/extraction/batch/{id}` - Estado del lote

### Exportación
- `POST /api/v1/export/excel` - Exportar a Excel
- `GET /api/v1/download/{filename}` - Descargar archivo

## 📝 Ejemplos de Uso

### Ejemplo: Extraer datos de facturas

1. **Plantilla Excel** con columnas:
   - Número de Factura
   - Fecha
   - Cliente
   - Total
   - IVA

2. **Documentos**: Fotos de facturas

3. **Resultado**: Excel con todos los datos extraídos

### Ejemplo: Procesar formularios

1. **Plantilla Word** con marcadores:
   - `{{nombre}}`
   - `{{email}}`
   - `{{telefono}}`

2. **Documentos**: Escaneos de formularios llenados

3. **Resultado**: Documentos Word rellenados

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **OpenAI GPT-4 Vision** - Análisis inteligente de imágenes
- **Tesseract OCR** - Reconocimiento de texto
- **OpenPyXL** - Manipulación de Excel
- **python-docx** - Manipulación de Word
- **Pillow/OpenCV** - Procesamiento de imágenes

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos utilitarios
- **Zustand** - Gestión de estado
- **Vite** - Build tool moderno

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [OpenAI](https://openai.com/) por GPT-4 Vision
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)

---

**DataExtractor AI** - Extracción inteligente de datos con IA 🚀
