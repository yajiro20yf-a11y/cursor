import { FileSpreadsheet, RefreshCw } from 'lucide-react';
import { useStore } from '../hooks/useStore';

export default function Header() {
  const { reset } = useStore();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <FileSpreadsheet className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">DataExtractor AI</h1>
              <p className="text-sm text-gray-500">Extracción inteligente de datos</p>
            </div>
          </div>
          
          <button
            onClick={reset}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Nuevo proceso</span>
          </button>
        </div>
      </div>
    </header>
  );
}
