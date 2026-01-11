import { useState } from 'react';
import { ArrowLeft, ArrowRight, Image, FileText, Trash2, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import FileDropzone from '../components/FileDropzone';
import { useStore } from '../hooks/useStore';
import { uploadDocuments, deleteDocument } from '../services/api';

export default function DocumentUpload() {
  const { 
    template, 
    documents, 
    addDocuments, 
    removeDocument, 
    nextStep, 
    prevStep,
    setIsLoading,
    isLoading 
  } = useStore();
  
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFilesAccepted = (files: File[]) => {
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveSelectedFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUploadFiles = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Selecciona al menos un archivo');
      return;
    }

    setUploading(true);

    try {
      const uploaded = await uploadDocuments(selectedFiles);
      addDocuments(uploaded);
      setSelectedFiles([]);
      toast.success(`${uploaded.length} documento(s) subido(s)`);
    } catch (error: any) {
      console.error('Error uploading documents:', error);
      toast.error(error.response?.data?.detail || 'Error al subir documentos');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveDocument = async (docId: string) => {
    try {
      await deleteDocument(docId);
      removeDocument(docId);
      toast.success('Documento eliminado');
    } catch (error) {
      toast.error('Error al eliminar documento');
    }
  };

  const handleContinue = () => {
    if (documents.length === 0) {
      toast.error('Sube al menos un documento para procesar');
      return;
    }
    nextStep();
  };

  const getFileIcon = (type: string) => {
    if (type === 'image') {
      return <Image className="w-5 h-5 text-green-600" />;
    }
    return <FileText className="w-5 h-5 text-blue-600" />;
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Subir Documentos</h2>
        <p className="mt-2 text-gray-600">
          Sube las fotos o escaneos de los documentos de donde quieres extraer los datos.
          Puedes subir múltiples archivos a la vez.
        </p>
      </div>

      {/* Resumen de plantilla */}
      {template && (
        <div className="mb-6 p-4 bg-primary-50 rounded-lg border border-primary-100">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-primary-600" />
            <div>
              <p className="font-medium text-primary-900">Plantilla: {template.name}</p>
              <p className="text-sm text-primary-700">
                {template.fields.length} campos configurados
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Dropzone */}
      <FileDropzone
        onFilesAccepted={handleFilesAccepted}
        accept={{
          'image/jpeg': ['.jpg', '.jpeg'],
          'image/png': ['.png'],
          'image/tiff': ['.tiff', '.tif'],
          'image/bmp': ['.bmp'],
          'application/pdf': ['.pdf'],
        }}
        maxFiles={50}
        multiple={true}
        label="Arrastra tus documentos aquí"
        description="Imágenes (JPG, PNG, TIFF) o PDFs escaneados"
        files={selectedFiles}
        onRemoveFile={handleRemoveSelectedFile}
      />

      {/* Botón de subir */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleUploadFiles}
            disabled={uploading}
            className="btn-success flex items-center gap-2"
          >
            {uploading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                Subir {selectedFiles.length} archivo(s)
              </>
            )}
          </button>
        </div>
      )}

      {/* Lista de documentos subidos */}
      {documents.length > 0 && (
        <div className="mt-8">
          <h3 className="font-semibold text-gray-900 mb-4">
            Documentos listos para procesar ({documents.length})
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {getFileIcon(doc.file_type)}
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {doc.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => handleRemoveDocument(doc.id)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navegación */}
      <div className="mt-8 flex justify-between">
        <button onClick={prevStep} className="btn-secondary flex items-center gap-2">
          <ArrowLeft className="w-5 h-5" />
          Anterior
        </button>
        
        <button
          onClick={handleContinue}
          disabled={documents.length === 0 || isLoading}
          className="btn-primary flex items-center gap-2"
        >
          Procesar
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
