# Makefile para DataExtractor AI

.PHONY: help install dev build docker-up docker-down clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install     - Instalar dependencias"
	@echo "  make dev         - Iniciar en modo desarrollo"
	@echo "  make build       - Construir para producción"
	@echo "  make docker-up   - Iniciar con Docker"
	@echo "  make docker-down - Detener Docker"
	@echo "  make clean       - Limpiar archivos temporales"

install:
	@echo "📦 Instalando dependencias del backend..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Instalando dependencias del frontend..."
	cd frontend && npm install
	@echo "✅ Instalación completada"

dev-backend:
	@echo "🚀 Iniciando backend..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-frontend:
	@echo "🚀 Iniciando frontend..."
	cd frontend && npm run dev

build:
	@echo "🏗️ Construyendo frontend..."
	cd frontend && npm run build
	@echo "✅ Build completado"

docker-up:
	@echo "🐳 Iniciando con Docker..."
	docker-compose up -d --build
	@echo "✅ Servicios iniciados"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

docker-down:
	@echo "🛑 Deteniendo Docker..."
	docker-compose down
	@echo "✅ Servicios detenidos"

clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	rm -rf uploads/* outputs/* 2>/dev/null || true
	@echo "✅ Limpieza completada"
