import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si es necesario
load_dotenv(override=True)

# Configuración de Azure OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Tu clave de API de Azure OpenAI
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  # URL del endpoint de Azure
DEPLOYMENT_NAME = "gpt-4o-mini"  # Nombre de tu deployment en Azure AI Foundry

# Crear el cliente de Azure OpenAI
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version="2023-12-01-preview",  # Usa la última versión de la API
    azure_endpoint=OPENAI_ENDPOINT
)

# Directorios de entrada y salida
INPUT_DIR = "fichas-json-clean/"
OUTPUT_DIR = "fichas-json-clean-structured/"
SCHEMA_PATH = "common_schema.json"  # Ruta del esquema común
os.makedirs(OUTPUT_DIR, exist_ok=True)

def restructure_json_with_openai(json_data, schema):
    """Envía el JSON a OpenAI para que lo reestructure según el esquema común."""
    prompt = (
        "Reestructura el siguiente JSON según el esquema común proporcionado.\n\n"
        "- **NO** modifiques el esquema común, solo organiza el JSON de acuerdo a él.\n\n"
        "- **NO** respondas con ningún texto, solo con cada JSON para poder guardarlo.\n\n"
        "Asegúrate de que el JSON resultante siga la estructura del esquema común.\n\n"
        f"Esquema común: {json.dumps(schema, ensure_ascii=False, indent=4)}\n\n"
        f"JSON: {json.dumps(json_data, ensure_ascii=False, indent=4)}"
    )
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[ 
            {"role": "system", "content": "Eres un asistente que organiza JSON según un esquema común."},
            {"role": "user", "content": prompt}
        ]
    )
    
    structured_json = response.choices[0].message.content
    print("Raw response from API:", structured_json)  # Depuración: Ver la respuesta cruda
    
    # Intentar convertir la respuesta en un JSON válido
    try:
        structured_json = json.loads(structured_json)
        print("JSON reestructurado:", json.dumps(structured_json, indent=4, ensure_ascii=False))  # Depuración: Ver el JSON reestructurado
        return structured_json
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print("Respuesta inválida del modelo:", structured_json)
        return None  # Retorna None si el JSON no es válido

# Cargar el esquema común
with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
    common_schema = json.load(schema_file)

# Procesar todos los archivos JSON en la carpeta de entrada
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)  # Usar el mismo nombre que el archivo original
        
        print(f"Procesando {filename}...")
        
        try:
            with open(input_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error: JSON inválido en {filename}. Saltando este archivo.")
            continue
        
        structured_data = restructure_json_with_openai(data, common_schema)
        
        if structured_data:  # Solo guardar si los datos estructurados son válidos
            try:
                with open(output_path, "w", encoding="utf-8") as outfile:
                    json.dump(structured_data, outfile, indent=4, ensure_ascii=False)
                print(f"Guardado en {output_path}")
            except Exception as e:
                print(f"Error al guardar el archivo {output_path}: {e}")

print("✅ Procesamiento completado.")
