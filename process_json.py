import json
import re

# Función recursiva para buscar los campos
def find_fields(data, fields_to_extract):
    result = {}
    
    # Si es un diccionario, buscamos los campos en él
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'fields':
                for field in fields_to_extract:
                    field_value = value.get(field, {}).get('valueString', '')
                    if field_value:
                        # Limpiar caracteres extraños y saltos de línea
                        cleaned_value = clean_text(field_value)
                        result[field] = cleaned_value
            else:
                # Llamamos a la función recursiva si el valor es otro diccionario o lista
                result.update(find_fields(value, fields_to_extract))
    
    # Si es una lista, buscamos en sus elementos
    elif isinstance(data, list):
        for item in data:
            result.update(find_fields(item, fields_to_extract))
    
    return result

# Función para limpiar caracteres extraños y saltos de línea
def clean_text(text):
    # Limpiar saltos de línea y espacios extra
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Cargar el archivo JSON original con la codificación adecuada
with open('fichas-json/17Z90R-E.AD78B.pdf.json', 'r', encoding="utf-8") as file:
    data = json.load(file)

# Lista de los campos que queremos extraer
fields_to_extract = [
    'Marca', 'Nombre', 'SistemaOperativo', 'Procesador', 'RAM', 'DiscoDuro', 
    'TarjetaGrafica', 'DimensionesPeso', 'Codigo', 'Precio', 'Pantalla', 
    'General', 'Conexiones', 'Audio', 'Bateria', 'Webcam', 'Teclado'
]

# Llamar a la función recursiva para extraer los campos
result = find_fields(data, fields_to_extract)

# Guardar el resultado en un nuevo archivo JSON con codificación UTF-8
with open('fichas-json-procesadas/17Z90R-E.AD78B.pdf.json', 'w', encoding="utf-8") as outfile:
    json.dump(result, outfile, indent=4, ensure_ascii=False)
