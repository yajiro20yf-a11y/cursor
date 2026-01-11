import { Toaster } from 'react-hot-toast';
import { useStore } from './hooks/useStore';
import Header from './components/Header';
import Stepper from './components/Stepper';
import TemplateUpload from './pages/TemplateUpload';
import FieldConfiguration from './pages/FieldConfiguration';
import DocumentUpload from './pages/DocumentUpload';
import Processing from './pages/Processing';
import Results from './pages/Results';

const steps = [
  { id: 0, name: 'Plantilla', description: 'Subir plantilla Excel/Word' },
  { id: 1, name: 'Campos', description: 'Configurar campos a extraer' },
  { id: 2, name: 'Documentos', description: 'Subir documentos fuente' },
  { id: 3, name: 'Procesar', description: 'Extraer datos con IA' },
  { id: 4, name: 'Resultados', description: 'Revisar y exportar' },
];

function App() {
  const { currentStep } = useStore();

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <TemplateUpload />;
      case 1:
        return <FieldConfiguration />;
      case 2:
        return <DocumentUpload />;
      case 3:
        return <Processing />;
      case 4:
        return <Results />;
      default:
        return <TemplateUpload />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Toaster position="top-right" />
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <Stepper steps={steps} currentStep={currentStep} />
        
        <div className="mt-8 animate-fade-in">
          {renderStep()}
        </div>
      </main>
      
      <footer className="py-6 text-center text-gray-500 text-sm">
        <p>DataExtractor AI - Extracción inteligente de datos</p>
      </footer>
    </div>
  );
}

export default App;
