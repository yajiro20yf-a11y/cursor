// Tipos principales de la aplicación

export type FieldType = 
  | 'text' 
  | 'number' 
  | 'date' 
  | 'email' 
  | 'phone' 
  | 'address' 
  | 'currency' 
  | 'percentage' 
  | 'custom';

export type ProcessingStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'error' 
  | 'partial';

export interface TemplateField {
  id: string;
  name: string;
  field_type: FieldType;
  description?: string;
  cell_reference?: string;
  column_index?: number;
  required: boolean;
  validation_pattern?: string;
  examples?: string[];
}

export interface FieldMapping {
  field_id: string;
  source_location?: string;
  confidence: number;
  extracted_value: any;
  validated: boolean;
}

export interface TemplateConfig {
  id: string;
  name: string;
  file_path: string;
  file_type: string;
  fields: TemplateField[];
  sheet_name?: string;
  start_row: number;
  created_at?: string;
  updated_at?: string;
}

export interface TemplateAnalysis {
  template_id: string;
  detected_fields: TemplateField[];
  suggested_mappings: Record<string, string>;
  sheet_names?: string[];
  preview_data?: Record<string, any>;
}

export interface DocumentUpload {
  id: string;
  filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  status: ProcessingStatus;
  extracted_text?: string;
  error_message?: string;
}

export interface ExtractionResult {
  document_id: string;
  document_name: string;
  fields: Record<string, FieldMapping>;
  raw_text?: string;
  confidence_score: number;
  processing_time_ms: number;
  status: ProcessingStatus;
  error_message?: string;
}

export interface ExtractionBatch {
  id: string;
  template_id: string;
  template_name: string;
  documents: DocumentUpload[];
  results: ExtractionResult[];
  status: ProcessingStatus;
  started_at?: string;
  completed_at?: string;
  total_documents: number;
  processed_documents: number;
  successful_extractions: number;
  output_file?: string;
}

// Estado de la aplicación
export interface AppState {
  // Paso actual del wizard
  currentStep: number;
  
  // Template
  template: TemplateConfig | null;
  templateAnalysis: TemplateAnalysis | null;
  
  // Documentos
  documents: DocumentUpload[];
  
  // Resultados
  extractionBatch: ExtractionBatch | null;
  
  // UI State
  isLoading: boolean;
  error: string | null;
}
