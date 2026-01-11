import openpyxl
import os
import shutil
from typing import Dict, Any, List

class ReportGenerator:
    def __init__(self, templates_dir: str = "documents/templates", output_dir: str = "documents/output"):
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, template_filename: str, data: Dict[str, Any], output_filename: str) -> str:
        """
        Toma una plantilla Excel, inyecta los datos en las celdas especificadas y guarda el resultado.
        
        Args:
            template_filename: Nombre del archivo en documents/templates (ej: "Factura_Master.xlsx")
            data: Diccionario con mapeo { "Celda": "Valor" } o { "CampoIA": "Valor" }
            output_filename: Nombre del archivo de salida
            
        Returns:
            Path absoluto del archivo generado.
        """
        template_path = os.path.join(self.templates_dir, template_filename)
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"No se encontró la plantilla: {template_path}")

        # 1. Cargar plantilla manteniendo estilos
        wb = openpyxl.load_workbook(template_path)
        
        # Asumimos que trabajamos en la primera hoja activa
        ws = wb.active
        
        # 2. Inyectar datos
        # Nota: Aquí asumimos que el 'key' del diccionario es la dirección de la celda (ej: 'B2')
        # Si el usuario mapeó "Nombre" -> "B2", el frontend debe enviarnos { "B2": "Juan" }
        # O debemos tener un paso intermedio de traducción. 
        # Para este ejemplo base, la IA intentará devolver claves que sean coordenadas o mapearemos dinámicamente.
        
        for cell_address, value in data.items():
            try:
                # Verificar si es una dirección de celda válida (ej: "B2", "AA10")
                if cell_address[0].isalpha() and any(c.isdigit() for c in cell_address):
                    ws[cell_address] = value
                else:
                    # Si la IA devolvió "Total_Factura": 500, y no sabemos dónde va, lo ignoramos o loggeamos
                    # En una versión avanzada, aquí consultaríamos el mapa de configuración del usuario
                    print(f"Campo '{cell_address}' no es una celda válida, omitiendo escritura.")
            except Exception as e:
                print(f"Error escribiendo en celda {cell_address}: {e}")

        # 3. Guardar
        wb.save(output_path)
        return output_path

    def batch_generate(self, template_filename: str, batch_data: List[Dict[str, Any]]) -> str:
        """
        Opcional: Si queremos generar UN solo Excel con muchas filas (tipo reporte consolidado).
        Esto dependerá de si el usuario quiere 1 archivo por foto o 1 archivo resumen.
        """
        pass
