import { useCallback } from 'react';
import { useDropzone, Accept } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import { clsx } from 'clsx';

interface FileDropzoneProps {
  onFilesAccepted: (files: File[]) => void;
  accept?: Accept;
  maxFiles?: number;
  maxSize?: number;
  multiple?: boolean;
  label?: string;
  description?: string;
  files?: File[];
  onRemoveFile?: (index: number) => void;
}

export default function FileDropzone({
  onFilesAccepted,
  accept,
  maxFiles = 50,
  maxSize = 50 * 1024 * 1024, // 50MB
  multiple = true,
  label = 'Arrastra archivos aquí',
  description = 'o haz clic para seleccionar',
  files = [],
  onRemoveFile,
}: FileDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onFilesAccepted(acceptedFiles);
    },
    [onFilesAccepted]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxFiles,
    maxSize,
    multiple,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
          isDragActive && !isDragReject
            ? 'border-primary-500 bg-primary-50'
            : isDragReject
            ? 'border-red-500 bg-red-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-3">
          <div
            className={clsx(
              'p-3 rounded-full',
              isDragActive ? 'bg-primary-100' : 'bg-gray-100'
            )}
          >
            <Upload
              className={clsx(
                'w-8 h-8',
                isDragActive ? 'text-primary-600' : 'text-gray-400'
              )}
            />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-700">{label}</p>
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          </div>
          
          {accept && (
            <p className="text-xs text-gray-400">
              Formatos: {Object.values(accept).flat().join(', ')}
            </p>
          )}
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">
            Archivos seleccionados ({files.length})
          </p>
          <ul className="divide-y divide-gray-100 border border-gray-200 rounded-lg overflow-hidden">
            {files.map((file, index) => (
              <li
                key={`${file.name}-${index}`}
                className="flex items-center justify-between px-4 py-3 bg-white hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <File className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-700 truncate max-w-xs">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                
                {onRemoveFile && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveFile(index);
                    }}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
