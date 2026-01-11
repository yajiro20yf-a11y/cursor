"""
Procesador de plantillas Excel y Word
Mantiene el formato original mientras agrega datos
"""
import os
import re
import copy
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.styles import Font, Alignment, Border, PatternFill
from docx import Document
from docx.shared import Inches, Pt
import pandas as pd

from ..config import settings
from ..models.schemas import (
    TemplateField, 
    TemplateConfig, 
    FieldType,
    ExtractionResult,
    TemplateAnalysis
)


class TemplateProcessor:
    """
    Procesador de plantillas Excel (.xlsx) y Word (.docx)
    Permite analizar, leer y escribir manteniendo el formato original
    """
    
    def __init__(self):
        """Inicializa el procesador de plantillas"""
        self.templates_dir = settings.TEMPLATES_DIR
        self.output_dir = settings.OUTPUT_DIR
    
    # ============= EXCEL PROCESSING =============
    
    def analyze_excel_template(
        self, 
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> TemplateAnalysis:
        """
        Analiza una plantilla Excel y detecta posibles campos
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja (opcional)
            
        Returns:
            Análisis de la plantilla con campos detectados
        """
        wb = load_workbook(file_path, data_only=False)
        
        # Obtener hojas disponibles
        sheet_names = wb.sheetnames
        
        # Seleccionar hoja
        if sheet_name and sheet_name in sheet_names:
            ws = wb[sheet_name]
        else:
            ws = wb.active
            sheet_name = ws.title
        
        detected_fields = []
        preview_data = {}
        
        # Analizar encabezados (primera fila con datos)
        header_row = None
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10), 1):
            non_empty = [cell for cell in row if cell.value is not None]
            if len(non_empty) >= 2:  # Al menos 2 celdas con datos
                header_row = row_idx
                break
        
        if header_row:
            for cell in ws[header_row]:
                if cell.value:
                    field_name = str(cell.value).strip()
                    cell_ref = f"{get_column_letter(cell.column)}{cell.row}"
                    
                    # Detectar tipo de campo basado en el nombre
                    field_type = self._detect_field_type(field_name)
                    
                    detected_fields.append(TemplateField(
                        id=self._generate_field_id(field_name),
                        name=field_name,
                        field_type=field_type,
                        cell_reference=cell_ref,
                        column_index=cell.column,
                        required=False
                    ))
                    
                    # Vista previa de datos existentes
                    preview_data[field_name] = []
                    for data_row in range(header_row + 1, min(header_row + 6, ws.max_row + 1)):
                        val = ws.cell(row=data_row, column=cell.column).value
                        if val is not None:
                            preview_data[field_name].append(str(val))
        
        # Detectar celdas con marcadores tipo {{campo}}
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    markers = re.findall(r'\{\{(\w+)\}\}', cell.value)
                    for marker in markers:
                        if not any(f.id == marker for f in detected_fields):
                            detected_fields.append(TemplateField(
                                id=marker,
                                name=marker.replace('_', ' ').title(),
                                field_type=FieldType.TEXT,
                                cell_reference=f"{get_column_letter(cell.column)}{cell.row}",
                                required=True
                            ))
        
        wb.close()
        
        return TemplateAnalysis(
            template_id=os.path.basename(file_path),
            detected_fields=detected_fields,
            suggested_mappings={},
            sheet_names=sheet_names,
            preview_data=preview_data
        )
    
    def _detect_field_type(self, field_name: str) -> FieldType:
        """Detecta el tipo de campo basado en su nombre"""
        name_lower = field_name.lower()
        
        if any(word in name_lower for word in ['email', 'correo', 'e-mail']):
            return FieldType.EMAIL
        elif any(word in name_lower for word in ['teléfono', 'telefono', 'phone', 'celular', 'móvil', 'movil']):
            return FieldType.PHONE
        elif any(word in name_lower for word in ['fecha', 'date', 'día', 'dia']):
            return FieldType.DATE
        elif any(word in name_lower for word in ['precio', 'costo', 'total', 'monto', 'importe', 'price', 'amount']):
            return FieldType.CURRENCY
        elif any(word in name_lower for word in ['porcentaje', 'percent', '%', 'tasa', 'rate']):
            return FieldType.PERCENTAGE
        elif any(word in name_lower for word in ['dirección', 'direccion', 'address', 'domicilio']):
            return FieldType.ADDRESS
        elif any(word in name_lower for word in ['cantidad', 'número', 'numero', 'qty', 'quantity', 'count']):
            return FieldType.NUMBER
        else:
            return FieldType.TEXT
    
    def _generate_field_id(self, name: str) -> str:
        """Genera un ID de campo a partir del nombre"""
        # Convertir a minúsculas y reemplazar espacios
        field_id = name.lower().strip()
        field_id = re.sub(r'[^a-záéíóúñ0-9\s]', '', field_id)
        field_id = re.sub(r'\s+', '_', field_id)
        return field_id
    
    def read_excel_template(
        self, 
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> Tuple[Workbook, Any]:
        """
        Lee una plantilla Excel preservando todo el formato
        
        Args:
            file_path: Ruta al archivo
            sheet_name: Nombre de la hoja
            
        Returns:
            Tupla (Workbook, Worksheet activa)
        """
        wb = load_workbook(file_path)
        
        if sheet_name and sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.active
        
        return wb, ws
    
    def fill_excel_template(
        self,
        template_path: str,
        extraction_results: List[ExtractionResult],
        template_config: TemplateConfig,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Rellena una plantilla Excel con los datos extraídos
        Mantiene el formato original
        
        Args:
            template_path: Ruta a la plantilla
            extraction_results: Resultados de extracción
            template_config: Configuración de la plantilla
            output_filename: Nombre del archivo de salida
            
        Returns:
            Ruta del archivo generado
        """
        wb, ws = self.read_excel_template(template_path, template_config.sheet_name)
        
        # Determinar fila inicial para datos
        start_row = template_config.start_row
        
        # Crear mapa de columnas
        column_map = {}
        for field in template_config.fields:
            if field.column_index:
                column_map[field.id] = field.column_index
            elif field.cell_reference:
                # Extraer columna de la referencia
                match = re.match(r'([A-Z]+)', field.cell_reference)
                if match:
                    column_map[field.id] = column_index_from_string(match.group(1))
        
        # Insertar datos
        for row_offset, result in enumerate(extraction_results):
            current_row = start_row + row_offset
            
            for field_id, mapping in result.fields.items():
                if field_id in column_map and mapping.extracted_value is not None:
                    col = column_map[field_id]
                    cell = ws.cell(row=current_row, column=col)
                    
                    # Preservar el formato de la celda de encabezado si existe
                    header_cell = ws.cell(row=start_row - 1, column=col)
                    
                    # Asignar valor
                    cell.value = mapping.extracted_value
                    
                    # Copiar formato básico de la fila anterior si existe
                    if current_row > start_row:
                        prev_cell = ws.cell(row=current_row - 1, column=col)
                        if prev_cell.number_format:
                            cell.number_format = prev_cell.number_format
        
        # Generar nombre de archivo de salida
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(template_path))[0]
            output_filename = f"{base_name}_filled_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        wb.save(output_path)
        wb.close()
        
        return output_path
    
    def fill_excel_with_markers(
        self,
        template_path: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Rellena una plantilla Excel que usa marcadores {{campo}}
        
        Args:
            template_path: Ruta a la plantilla
            data: Diccionario con datos a insertar
            output_filename: Nombre del archivo de salida
            
        Returns:
            Ruta del archivo generado
        """
        wb = load_workbook(template_path)
        
        for sheet in wb.worksheets:
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        # Reemplazar marcadores
                        new_value = cell.value
                        for key, value in data.items():
                            marker = f"{{{{{key}}}}}"
                            if marker in new_value:
                                new_value = new_value.replace(marker, str(value) if value else "")
                        
                        if new_value != cell.value:
                            cell.value = new_value
        
        # Generar nombre de archivo
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(template_path))[0]
            output_filename = f"{base_name}_filled_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        wb.save(output_path)
        wb.close()
        
        return output_path
    
    def append_to_excel(
        self,
        excel_path: str,
        extraction_results: List[ExtractionResult],
        template_config: TemplateConfig
    ) -> str:
        """
        Agrega datos a un Excel existente sin sobrescribir
        
        Args:
            excel_path: Ruta al archivo Excel
            extraction_results: Resultados de extracción
            template_config: Configuración de la plantilla
            
        Returns:
            Ruta del archivo actualizado
        """
        wb, ws = self.read_excel_template(excel_path, template_config.sheet_name)
        
        # Encontrar la última fila con datos
        last_row = ws.max_row
        
        # Si la última fila es la de encabezados, empezar después
        if last_row < template_config.start_row:
            last_row = template_config.start_row - 1
        
        # Crear mapa de columnas
        column_map = {}
        for field in template_config.fields:
            if field.column_index:
                column_map[field.id] = field.column_index
        
        # Agregar nuevos datos
        for row_offset, result in enumerate(extraction_results):
            current_row = last_row + 1 + row_offset
            
            for field_id, mapping in result.fields.items():
                if field_id in column_map and mapping.extracted_value is not None:
                    col = column_map[field_id]
                    ws.cell(row=current_row, column=col, value=mapping.extracted_value)
        
        wb.save(excel_path)
        wb.close()
        
        return excel_path
    
    # ============= WORD PROCESSING =============
    
    def analyze_word_template(self, file_path: str) -> TemplateAnalysis:
        """
        Analiza una plantilla Word y detecta marcadores
        
        Args:
            file_path: Ruta al archivo Word
            
        Returns:
            Análisis de la plantilla
        """
        doc = Document(file_path)
        detected_fields = []
        
        # Buscar marcadores en párrafos
        for para in doc.paragraphs:
            markers = re.findall(r'\{\{(\w+)\}\}', para.text)
            for marker in markers:
                if not any(f.id == marker for f in detected_fields):
                    detected_fields.append(TemplateField(
                        id=marker,
                        name=marker.replace('_', ' ').title(),
                        field_type=self._detect_field_type(marker),
                        required=True
                    ))
        
        # Buscar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    markers = re.findall(r'\{\{(\w+)\}\}', cell.text)
                    for marker in markers:
                        if not any(f.id == marker for f in detected_fields):
                            detected_fields.append(TemplateField(
                                id=marker,
                                name=marker.replace('_', ' ').title(),
                                field_type=self._detect_field_type(marker),
                                required=True
                            ))
        
        return TemplateAnalysis(
            template_id=os.path.basename(file_path),
            detected_fields=detected_fields,
            suggested_mappings={}
        )
    
    def fill_word_template(
        self,
        template_path: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Rellena una plantilla Word con datos
        
        Args:
            template_path: Ruta a la plantilla
            data: Diccionario con datos
            output_filename: Nombre del archivo de salida
            
        Returns:
            Ruta del archivo generado
        """
        doc = Document(template_path)
        
        # Reemplazar en párrafos
        for para in doc.paragraphs:
            self._replace_markers_in_paragraph(para, data)
        
        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._replace_markers_in_paragraph(para, data)
        
        # Generar nombre de archivo
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(template_path))[0]
            output_filename = f"{base_name}_filled_{timestamp}.docx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        doc.save(output_path)
        
        return output_path
    
    def _replace_markers_in_paragraph(self, para, data: Dict[str, Any]):
        """Reemplaza marcadores en un párrafo preservando formato"""
        for key, value in data.items():
            marker = f"{{{{{key}}}}}"
            if marker in para.text:
                # Preservar formato del primer run
                for run in para.runs:
                    if marker in run.text:
                        run.text = run.text.replace(marker, str(value) if value else "")
    
    # ============= UTILITY METHODS =============
    
    def export_results_to_excel(
        self,
        extraction_results: List[ExtractionResult],
        fields: List[TemplateField],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Exporta resultados de extracción a un nuevo Excel
        
        Args:
            extraction_results: Resultados de extracción
            fields: Definición de campos
            output_filename: Nombre del archivo
            
        Returns:
            Ruta del archivo generado
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Datos Extraídos"
        
        # Crear encabezados
        headers = ["Documento"] + [field.name for field in fields] + ["Confianza Promedio"]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        
        # Agregar datos
        for row_idx, result in enumerate(extraction_results, 2):
            ws.cell(row=row_idx, column=1, value=result.document_name)
            
            confidences = []
            for col_idx, field in enumerate(fields, 2):
                mapping = result.fields.get(field.id)
                if mapping:
                    ws.cell(row=row_idx, column=col_idx, value=mapping.extracted_value)
                    confidences.append(mapping.confidence)
            
            # Confianza promedio
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            ws.cell(row=row_idx, column=len(headers), value=f"{avg_confidence:.2%}")
        
        # Ajustar ancho de columnas
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 20
        
        # Generar nombre de archivo
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"extraction_results_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_dir, output_filename)
        wb.save(output_path)
        wb.close()
        
        return output_path


# Instancia global
template_processor = TemplateProcessor()
