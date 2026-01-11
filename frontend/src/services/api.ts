import axios from 'axios';
import type { 
  TemplateAnalysis, 
  TemplateConfig, 
  DocumentUpload, 
  ExtractionBatch,
  ExtractionResult,
  TemplateField
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============= PLANTILLAS =============

export async function uploadTemplate(file: File, templateName?: string): Promise<TemplateAnalysis> {
  const formData = new FormData();
  formData.append('file', file);
  if (templateName) {
    formData.append('template_name', templateName);
  }

  const response = await api.post<TemplateAnalysis>('/templates/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  return response.data;
}

export async function configureTemplate(
  templateId: string,
  templateName: string,
  fields: TemplateField[],
  sheetName?: string,
  startRow: number = 2
): Promise<TemplateConfig> {
  const formData = new FormData();
  formData.append('template_id', templateId);
  formData.append('template_name', templateName);
  formData.append('fields', JSON.stringify(fields));
  if (sheetName) {
    formData.append('sheet_name', sheetName);
  }
  formData.append('start_row', startRow.toString());

  const response = await api.post<TemplateConfig>('/templates/configure', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  return response.data;
}

export async function analyzeTemplate(
  templateId: string, 
  sheetName?: string
): Promise<TemplateAnalysis> {
  const params = sheetName ? { sheet_name: sheetName } : {};
  const response = await api.get<TemplateAnalysis>(
    `/templates/${templateId}/analyze`, 
    { params }
  );
  return response.data;
}

// ============= DOCUMENTOS =============

export async function uploadDocuments(files: File[]): Promise<DocumentUpload[]> {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await api.post<DocumentUpload[]>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`);
}

// ============= EXTRACCIÓN =============

export async function processExtraction(
  templateConfig: TemplateConfig,
  documentIds: string[],
  useAI: boolean = true
): Promise<ExtractionBatch> {
  const response = await api.post<ExtractionBatch>('/extraction/process', {
    template_config: templateConfig,
    document_ids: documentIds,
    use_ai: useAI,
  });
  
  return response.data;
}

export async function processSingleDocument(
  documentId: string,
  fields: TemplateField[],
  useAI: boolean = true
): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append('document_id', documentId);
  formData.append('fields', JSON.stringify(fields));
  formData.append('use_ai', useAI.toString());

  const response = await api.post<ExtractionResult>('/extraction/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  
  return response.data;
}

export async function getBatchStatus(batchId: string): Promise<ExtractionBatch> {
  const response = await api.get<ExtractionBatch>(`/extraction/batch/${batchId}`);
  return response.data;
}

// ============= EXPORTACIÓN =============

export async function exportToExcel(
  batchId: string,
  templateConfig: TemplateConfig
): Promise<Blob> {
  const formData = new FormData();
  formData.append('batch_id', batchId);
  formData.append('template_config', JSON.stringify(templateConfig));

  const response = await api.post('/export/excel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob',
  });
  
  return response.data;
}

export async function downloadFile(filename: string): Promise<Blob> {
  const response = await api.get(`/download/${filename}`, {
    responseType: 'blob',
  });
  return response.data;
}

// ============= UTILIDADES =============

export async function healthCheck(): Promise<{
  status: string;
  version: string;
  services: Record<string, string>;
}> {
  const response = await api.get('/health');
  return response.data;
}

export async function getFieldTypes(): Promise<Array<{ value: string; label: string }>> {
  const response = await api.get('/field-types');
  return response.data;
}

export default api;
