import json
import os
import re

# Directorios de entrada y salida
dir_input = 'fichas-json/'
dir_output = 'fichas-json-clean/'

# Lista de los campos que queremos extraer
fields_to_extract = [
    'Marca', 'Nombre', 'SistemaOperativo', 'Procesador', 'RAM', 'DiscoDuro', 
    'TarjetaGrafica', 'DimensionesPeso', 'Codigo', 'Precio', 'Pantalla', 
    'General', 'Conexiones', 'Audio', 'Bateria', 'Webcam', 'Teclado', 'Alimentador'
]

# Función recursiva para buscar los campos
def find_fields(data, fields_to_extract):
    result = {field: '' for field in fields_to_extract}  # Inicializar con valores vacíos
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'fields':
                for field in fields_to_extract:
                    field_value = value.get(field, {}).get('valueString', '')
                    if field_value:
                        result[field] = clean_text(field_value)
            else:
                result.update({k: v for k, v in find_fields(value, fields_to_extract).items() if v})
    elif isinstance(data, list):
        for item in data:
            result.update({k: v for k, v in find_fields(item, fields_to_extract).items() if v})
    
    return result

# Función para limpiar caracteres extraños y saltos de línea
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Asegurar que el directorio de salida existe
os.makedirs(dir_output, exist_ok=True)

# Procesar todos los archivos JSON en el directorio de entrada
for filename in os.listdir(dir_input):
    if filename.endswith('.json'):
        input_path = os.path.join(dir_input, filename)
        output_path = os.path.join(dir_output, filename)
        
        with open(input_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        result = find_fields(data, fields_to_extract)
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(result, outfile, indent=4, ensure_ascii=False)

print("Procesamiento completado.")
