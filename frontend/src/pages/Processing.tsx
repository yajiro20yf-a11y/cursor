import { useState, useEffect } from 'react';
import { Cpu, CheckCircle, XCircle, Clock, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { useStore } from '../hooks/useStore';
import { processExtraction } from '../services/api';

export default function Processing() {
  const { 
    template, 
    documents, 
    setExtractionBatch, 
    nextStep, 
    prevStep 
  } = useStore();
  
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentDoc, setCurrentDoc] = useState('');
  const [useAI, setUseAI] = useState(true);
  const [started, setStarted] = useState(false);

  const handleStartProcessing = async () => {
    if (!template || documents.length === 0) {
      toast.error('Configuración incompleta');
      return;
    }

    setProcessing(true);
    setStarted(true);
    setProgress(0);

    // Simular progreso visual
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 10;
      });
    }, 500);

    // Actualizar documento actual
    let docIndex = 0;
    const docInterval = setInterval(() => {
      if (docIndex < documents.length) {
        setCurrentDoc(documents[docIndex].filename);
        docIndex++;
      }
    }, 2000);

    try {
      const batch = await processExtraction(
        template,
        documents.map((d) => d.id),
        useAI
      );

      clearInterval(progressInterval);
      clearInterval(docInterval);
      setProgress(100);

      setExtractionBatch(batch);
      
      toast.success(
        `Procesados ${batch.successful_extractions} de ${batch.total_documents} documentos`
      );

      // Pequeña pausa para mostrar 100%
      setTimeout(() => {
        nextStep();
      }, 500);
      
    } catch (error: any) {
      clearInterval(progressInterval);
      clearInterval(docInterval);
      console.error('Error processing:', error);
      toast.error(error.response?.data?.detail || 'Error en el procesamiento');
      setProcessing(false);
    }
  };

  if (!template || documents.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">Configuración incompleta</p>
        <button onClick={prevStep} className="btn-secondary mt-4">
          Volver
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Procesar Documentos</h2>
        <p className="mt-2 text-gray-600">
          La IA analizará cada documento y extraerá los datos según los campos configurados.
        </p>
      </div>

      {/* Resumen */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
          <p className="text-sm text-blue-600">Plantilla</p>
          <p className="font-semibold text-blue-900">{template.name}</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg border border-green-100">
          <p className="text-sm text-green-600">Documentos</p>
          <p className="font-semibold text-green-900">{documents.length} archivos</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
          <p className="text-sm text-purple-600">Campos</p>
          <p className="font-semibold text-purple-900">{template.fields.length} campos</p>
        </div>
      </div>

      {!started ? (
        <>
          {/* Opciones de procesamiento */}
          <div className="mb-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-4">Opciones de procesamiento</h3>
            
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
              />
              <div>
                <span className="font-medium text-gray-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  Usar extracción con IA (GPT-4 Vision)
                </span>
                <p className="text-sm text-gray-500">
                  Mayor precisión al analizar documentos complejos
                </p>
              </div>
            </label>
          </div>

          {/* Botón de inicio */}
          <div className="text-center">
            <button
              onClick={handleStartProcessing}
              className="btn-primary text-lg px-8 py-3 flex items-center gap-3 mx-auto"
            >
              <Cpu className="w-6 h-6" />
              Iniciar Procesamiento
            </button>
          </div>
        </>
      ) : (
        <>
          {/* Progreso */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Progreso</span>
              <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Estado actual */}
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-100 rounded-full mb-4">
              <Cpu className="w-10 h-10 text-primary-600 animate-pulse" />
            </div>
            
            <p className="text-lg font-medium text-gray-900">
              {progress < 100 ? 'Procesando...' : '¡Completado!'}
            </p>
            
            {currentDoc && progress < 100 && (
              <p className="text-sm text-gray-500 mt-2 flex items-center justify-center gap-2">
                <Clock className="w-4 h-4" />
                Analizando: {currentDoc}
              </p>
            )}
          </div>

          {/* Lista de documentos */}
          <div className="mt-6 space-y-2">
            {documents.map((doc, index) => {
              const processed = (progress / 100) * documents.length > index;
              const current = Math.floor((progress / 100) * documents.length) === index;
              
              return (
                <div
                  key={doc.id}
                  className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    processed
                      ? 'bg-green-50 border border-green-100'
                      : current
                      ? 'bg-blue-50 border border-blue-100'
                      : 'bg-gray-50 border border-gray-100'
                  }`}
                >
                  {processed ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : current ? (
                    <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Clock className="w-5 h-5 text-gray-400" />
                  )}
                  <span
                    className={`text-sm ${
                      processed ? 'text-green-700' : current ? 'text-blue-700' : 'text-gray-500'
                    }`}
                  >
                    {doc.filename}
                  </span>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
