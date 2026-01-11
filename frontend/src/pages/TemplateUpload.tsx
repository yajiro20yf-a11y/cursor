import { useState } from 'react';
import { FileSpreadsheet, FileText, ArrowRight, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import FileDropzone from '../components/FileDropzone';
import { useStore } from '../hooks/useStore';
import { uploadTemplate } from '../services/api';

export default function TemplateUpload() {
  const { setTemplateAnalysis, nextStep, setIsLoading, isLoading } = useStore();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFilesAccepted = (files: File[]) => {
    // Solo permitir un archivo de plantilla
    if (files.length > 0) {
      setSelectedFiles([files[0]]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFiles([]);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Por favor selecciona una plantilla');
      return;
    }

    setIsLoading(true);
    
    try {
      const analysis = await uploadTemplate(selectedFiles[0]);
      setTemplateAnalysis(analysis);
      toast.success('Plantilla analizada correctamente');
      nextStep();
    } catch (error: any) {
      console.error('Error uploading template:', error);
      toast.error(error.response?.data?.detail || 'Error al subir la plantilla');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Subir Plantilla</h2>
        <p className="mt-2 text-gray-600">
          Sube tu plantilla Excel o Word. El sistema analizará su estructura para
          detectar los campos que puedes extraer.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="flex items-start gap-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <FileSpreadsheet className="w-8 h-8 text-blue-600 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900">Excel (.xlsx)</h3>
            <p className="text-sm text-blue-700 mt-1">
              Plantillas con columnas definidas para cada campo de datos.
              Ideal para listas y tablas.
            </p>
          </div>
        </div>
        
        <div className="flex items-start gap-4 p-4 bg-purple-50 rounded-lg border border-purple-100">
          <FileText className="w-8 h-8 text-purple-600 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-purple-900">Word (.docx)</h3>
            <p className="text-sm text-purple-700 mt-1">
              Plantillas con marcadores {'{{campo}}'} para documentos formateados.
            </p>
          </div>
        </div>
      </div>

      <FileDropzone
        onFilesAccepted={handleFilesAccepted}
        accept={{
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        }}
        maxFiles={1}
        multiple={false}
        label="Arrastra tu plantilla aquí"
        description="Formatos soportados: Excel (.xlsx) o Word (.docx)"
        files={selectedFiles}
        onRemoveFile={handleRemoveFile}
      />

      <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-100 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-800">
          <p className="font-medium">Consejo:</p>
          <p className="mt-1">
            Para Excel: asegúrate de que la primera fila contenga los nombres de las columnas.
            Para Word: usa marcadores como {'{{nombre}}'}, {'{{fecha}}'}, etc.
          </p>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button
          onClick={handleUpload}
          disabled={selectedFiles.length === 0 || isLoading}
          className="btn-primary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analizando...
            </>
          ) : (
            <>
              Continuar
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
