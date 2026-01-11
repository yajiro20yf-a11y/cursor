"""
DataExtractor AI - Aplicación Principal
Extracción inteligente de datos de documentos a plantillas Excel/Word
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .api.routes import router


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## DataExtractor AI
    
    Sistema inteligente para extraer datos de documentos escaneados y fotos,
    y agregarlos automáticamente a plantillas Excel o Word.
    
    ### Funcionalidades principales:
    
    - **📄 Plantillas**: Sube plantillas Excel/Word y define los campos a extraer
    - **📷 Documentos**: Procesa múltiples imágenes o PDFs escaneados
    - **🤖 IA**: Extracción inteligente usando OCR y GPT-4 Vision
    - **📊 Exportación**: Genera archivos Excel con los datos extraídos
    
    ### Flujo de trabajo:
    
    1. Sube una plantilla Excel/Word
    2. Selecciona los campos que quieres extraer
    3. Sube los documentos fuente (fotos, escaneos)
    4. La IA extrae los datos automáticamente
    5. Descarga el archivo con todos los datos
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio de archivos estáticos (para outputs)
if os.path.exists(settings.OUTPUT_DIR):
    app.mount("/files", StaticFiles(directory=settings.OUTPUT_DIR), name="files")

# Incluir rutas de la API
app.include_router(router, prefix="/api/v1", tags=["DataExtractor"])


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    print(f"📁 Directorio de uploads: {settings.UPLOAD_DIR}")
    print(f"📁 Directorio de plantillas: {settings.TEMPLATES_DIR}")
    print(f"📁 Directorio de salidas: {settings.OUTPUT_DIR}")
    
    if settings.OPENAI_API_KEY:
        print("🤖 OpenAI API configurada")
    else:
        print("⚠️  OpenAI API no configurada - usando solo OCR básico")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    print(f"👋 {settings.APP_NAME} detenido")
