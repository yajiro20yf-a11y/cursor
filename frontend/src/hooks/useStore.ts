import { create } from 'zustand';
import type { 
  TemplateConfig, 
  TemplateAnalysis, 
  DocumentUpload, 
  ExtractionBatch,
  TemplateField 
} from '../types';

interface AppStore {
  // Estado del wizard
  currentStep: number;
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  
  // Template
  template: TemplateConfig | null;
  templateAnalysis: TemplateAnalysis | null;
  setTemplate: (template: TemplateConfig | null) => void;
  setTemplateAnalysis: (analysis: TemplateAnalysis | null) => void;
  updateTemplateFields: (fields: TemplateField[]) => void;
  
  // Documentos
  documents: DocumentUpload[];
  setDocuments: (docs: DocumentUpload[]) => void;
  addDocuments: (docs: DocumentUpload[]) => void;
  removeDocument: (id: string) => void;
  
  // Resultados
  extractionBatch: ExtractionBatch | null;
  setExtractionBatch: (batch: ExtractionBatch | null) => void;
  
  // UI
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
  
  // Reset
  reset: () => void;
}

const initialState = {
  currentStep: 0,
  template: null,
  templateAnalysis: null,
  documents: [],
  extractionBatch: null,
  isLoading: false,
  error: null,
};

export const useStore = create<AppStore>((set, get) => ({
  ...initialState,
  
  // Navegación
  setCurrentStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: Math.min(state.currentStep + 1, 4) })),
  prevStep: () => set((state) => ({ currentStep: Math.max(state.currentStep - 1, 0) })),
  
  // Template
  setTemplate: (template) => set({ template }),
  setTemplateAnalysis: (analysis) => set({ templateAnalysis: analysis }),
  updateTemplateFields: (fields) => set((state) => ({
    template: state.template ? { ...state.template, fields } : null
  })),
  
  // Documentos
  setDocuments: (documents) => set({ documents }),
  addDocuments: (docs) => set((state) => ({ 
    documents: [...state.documents, ...docs] 
  })),
  removeDocument: (id) => set((state) => ({
    documents: state.documents.filter(d => d.id !== id)
  })),
  
  // Resultados
  setExtractionBatch: (batch) => set({ extractionBatch: batch }),
  
  // UI
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  
  // Reset
  reset: () => set(initialState),
}));
