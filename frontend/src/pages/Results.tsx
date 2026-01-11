import { useState } from 'react';
import { 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  FileSpreadsheet,
  Eye,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useStore } from '../hooks/useStore';
import { exportToExcel } from '../services/api';

export default function Results() {
  const { extractionBatch, template, reset } = useStore();
  const [exporting, setExporting] = useState(false);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());

  if (!extractionBatch || !template) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">No hay resultados disponibles</p>
        <button onClick={reset} className="btn-primary mt-4">
          Comenzar nuevo proceso
        </button>
      </div>
    );
  }

  const toggleExpanded = (docId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(docId)) {
      newExpanded.delete(docId);
    } else {
      newExpanded.add(docId);
    }
    setExpandedResults(newExpanded);
  };

  const handleExport = async () => {
    setExporting(true);
    
    try {
      const blob = await exportToExcel(extractionBatch.id, template);
      
      // Descargar archivo
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${template.name}_datos_extraidos.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Archivo descargado correctamente');
    } catch (error: any) {
      console.error('Error exporting:', error);
      toast.error('Error al exportar archivo');
    } finally {
      setExporting(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.5) return 'text-amber-600 bg-amber-100';
    return 'text-red-600 bg-red-100';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-amber-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Resumen */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Resultados de Extracción</h2>
            <p className="mt-1 text-gray-600">
              Revisa los datos extraídos y descarga el archivo Excel
            </p>
          </div>
          
          <button
            onClick={handleExport}
            disabled={exporting}
            className="btn-success flex items-center gap-2"
          >
            {exporting ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Exportando...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Descargar Excel
              </>
            )}
          </button>
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg text-center">
            <p className="text-3xl font-bold text-blue-600">
              {extractionBatch.total_documents}
            </p>
            <p className="text-sm text-blue-700">Total documentos</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg text-center">
            <p className="text-3xl font-bold text-green-600">
              {extractionBatch.successful_extractions}
            </p>
            <p className="text-sm text-green-700">Exitosos</p>
          </div>
          
          <div className="p-4 bg-red-50 rounded-lg text-center">
            <p className="text-3xl font-bold text-red-600">
              {extractionBatch.total_documents - extractionBatch.successful_extractions}
            </p>
            <p className="text-sm text-red-700">Con errores</p>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg text-center">
            <p className="text-3xl font-bold text-purple-600">
              {template.fields.length}
            </p>
            <p className="text-sm text-purple-700">Campos extraídos</p>
          </div>
        </div>
      </div>

      {/* Resultados detallados */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Detalle por documento
        </h3>
        
        <div className="space-y-3">
          {extractionBatch.results.map((result) => (
            <div
              key={result.document_id}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              {/* Header del resultado */}
              <div
                className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleExpanded(result.document_id)}
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(result.status)}
                  <div>
                    <p className="font-medium text-gray-900">{result.document_name}</p>
                    <p className="text-sm text-gray-500">
                      Procesado en {result.processing_time_ms}ms
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <span
                    className={`px-2 py-1 rounded text-sm font-medium ${getConfidenceColor(
                      result.confidence_score
                    )}`}
                  >
                    {(result.confidence_score * 100).toFixed(0)}% confianza
                  </span>
                  
                  {expandedResults.has(result.document_id) ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>
              
              {/* Detalles expandidos */}
              {expandedResults.has(result.document_id) && (
                <div className="p-4 border-t border-gray-200">
                  {result.status === 'error' ? (
                    <div className="p-3 bg-red-50 rounded-lg text-red-700">
                      <p className="font-medium">Error:</p>
                      <p className="text-sm">{result.error_message}</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {template.fields.map((field) => {
                        const mapping = result.fields[field.id];
                        return (
                          <div
                            key={field.id}
                            className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div className="min-w-0">
                              <p className="text-sm font-medium text-gray-700">
                                {field.name}
                              </p>
                              <p className="text-base text-gray-900 truncate">
                                {mapping?.extracted_value ?? (
                                  <span className="text-gray-400 italic">No encontrado</span>
                                )}
                              </p>
                            </div>
                            {mapping && (
                              <span
                                className={`ml-2 px-2 py-0.5 rounded text-xs font-medium flex-shrink-0 ${getConfidenceColor(
                                  mapping.confidence
                                )}`}
                              >
                                {(mapping.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Acciones finales */}
      <div className="card">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <FileSpreadsheet className="w-10 h-10 text-green-600" />
            <div>
              <p className="font-medium text-gray-900">
                Archivo listo para descargar
              </p>
              <p className="text-sm text-gray-500">
                {template.name}_datos_extraidos.xlsx
              </p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={reset}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Nuevo proceso
            </button>
            
            <button
              onClick={handleExport}
              disabled={exporting}
              className="btn-primary flex items-center gap-2"
            >
              <Download className="w-5 h-5" />
              Descargar Excel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
