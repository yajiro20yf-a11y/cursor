import { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Plus, Trash2, GripVertical, Settings2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useStore } from '../hooks/useStore';
import { configureTemplate } from '../services/api';
import type { TemplateField, FieldType } from '../types';

const FIELD_TYPES: { value: FieldType; label: string }[] = [
  { value: 'text', label: 'Texto' },
  { value: 'number', label: 'Número' },
  { value: 'date', label: 'Fecha' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Teléfono' },
  { value: 'address', label: 'Dirección' },
  { value: 'currency', label: 'Moneda' },
  { value: 'percentage', label: 'Porcentaje' },
  { value: 'custom', label: 'Personalizado' },
];

export default function FieldConfiguration() {
  const { 
    templateAnalysis, 
    setTemplate, 
    nextStep, 
    prevStep, 
    setIsLoading, 
    isLoading 
  } = useStore();
  
  const [fields, setFields] = useState<TemplateField[]>([]);
  const [templateName, setTemplateName] = useState('');
  const [selectedSheet, setSelectedSheet] = useState<string>('');
  const [startRow, setStartRow] = useState(2);

  useEffect(() => {
    if (templateAnalysis) {
      setFields(templateAnalysis.detected_fields);
      setTemplateName(templateAnalysis.template_id);
      if (templateAnalysis.sheet_names && templateAnalysis.sheet_names.length > 0) {
        setSelectedSheet(templateAnalysis.sheet_names[0]);
      }
    }
  }, [templateAnalysis]);

  const handleFieldChange = (index: number, key: keyof TemplateField, value: any) => {
    const updated = [...fields];
    updated[index] = { ...updated[index], [key]: value };
    setFields(updated);
  };

  const handleToggleRequired = (index: number) => {
    const updated = [...fields];
    updated[index] = { ...updated[index], required: !updated[index].required };
    setFields(updated);
  };

  const handleRemoveField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index));
  };

  const handleAddField = () => {
    const newField: TemplateField = {
      id: `field_${Date.now()}`,
      name: 'Nuevo Campo',
      field_type: 'text',
      required: false,
    };
    setFields([...fields, newField]);
  };

  const handleConfigure = async () => {
    if (fields.length === 0) {
      toast.error('Debes definir al menos un campo');
      return;
    }

    if (!templateName.trim()) {
      toast.error('Ingresa un nombre para la plantilla');
      return;
    }

    setIsLoading(true);

    try {
      const config = await configureTemplate(
        templateAnalysis!.template_id,
        templateName,
        fields,
        selectedSheet || undefined,
        startRow
      );
      
      setTemplate(config);
      toast.success('Configuración guardada');
      nextStep();
    } catch (error: any) {
      console.error('Error configuring template:', error);
      toast.error(error.response?.data?.detail || 'Error al configurar la plantilla');
    } finally {
      setIsLoading(false);
    }
  };

  if (!templateAnalysis) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">No hay plantilla cargada</p>
        <button onClick={prevStep} className="btn-secondary mt-4">
          Volver
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Configurar Campos</h2>
        <p className="mt-2 text-gray-600">
          Selecciona y configura los campos que quieres extraer de los documentos.
        </p>
      </div>

      {/* Configuración general */}
      <div className="grid md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div>
          <label className="label">Nombre de plantilla</label>
          <input
            type="text"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            className="input"
            placeholder="Ej: Facturas 2024"
          />
        </div>
        
        {templateAnalysis.sheet_names && templateAnalysis.sheet_names.length > 1 && (
          <div>
            <label className="label">Hoja de Excel</label>
            <select
              value={selectedSheet}
              onChange={(e) => setSelectedSheet(e.target.value)}
              className="input"
            >
              {templateAnalysis.sheet_names.map((sheet) => (
                <option key={sheet} value={sheet}>
                  {sheet}
                </option>
              ))}
            </select>
          </div>
        )}
        
        <div>
          <label className="label">Fila inicial de datos</label>
          <input
            type="number"
            value={startRow}
            onChange={(e) => setStartRow(parseInt(e.target.value) || 2)}
            min={1}
            className="input"
          />
        </div>
      </div>

      {/* Lista de campos */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Settings2 className="w-5 h-5" />
          Campos a extraer ({fields.length})
        </h3>
        <button onClick={handleAddField} className="btn-secondary text-sm flex items-center gap-1">
          <Plus className="w-4 h-4" />
          Agregar campo
        </button>
      </div>

      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
          >
            <GripVertical className="w-5 h-5 text-gray-300 cursor-grab" />
            
            <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3">
              <input
                type="text"
                value={field.name}
                onChange={(e) => handleFieldChange(index, 'name', e.target.value)}
                placeholder="Nombre del campo"
                className="input text-sm"
              />
              
              <select
                value={field.field_type}
                onChange={(e) => handleFieldChange(index, 'field_type', e.target.value)}
                className="input text-sm"
              >
                {FIELD_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              
              <input
                type="text"
                value={field.description || ''}
                onChange={(e) => handleFieldChange(index, 'description', e.target.value)}
                placeholder="Descripción (ayuda a la IA)"
                className="input text-sm"
              />
              
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={field.required}
                    onChange={() => handleToggleRequired(index)}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-600">Requerido</span>
                </label>
              </div>
            </div>
            
            <button
              onClick={() => handleRemoveField(index)}
              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>

      {fields.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No hay campos configurados.</p>
          <button onClick={handleAddField} className="btn-primary mt-4">
            Agregar primer campo
          </button>
        </div>
      )}

      {/* Vista previa de datos */}
      {templateAnalysis.preview_data && Object.keys(templateAnalysis.preview_data).length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Vista previa de datos existentes:</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            {Object.entries(templateAnalysis.preview_data).slice(0, 8).map(([key, values]) => (
              <div key={key} className="bg-white p-2 rounded">
                <span className="font-medium text-blue-800">{key}:</span>
                <span className="text-blue-600 ml-1">
                  {Array.isArray(values) ? values[0] || '-' : String(values)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 flex justify-between">
        <button onClick={prevStep} className="btn-secondary flex items-center gap-2">
          <ArrowLeft className="w-5 h-5" />
          Anterior
        </button>
        
        <button
          onClick={handleConfigure}
          disabled={fields.length === 0 || isLoading}
          className="btn-primary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Guardando...
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
