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
os.makedirs(OUTPUT_DIR, exist_ok=True)

def restructure_json_with_openai(json_data):
    """Envía el JSON a OpenAI para que lo reestructure."""
    prompt = (
        "Reestructura el siguiente JSON de manera lógica y organizada en categorías anidadas. "
        "Agrupa especificaciones similares sin eliminar información. Devuelve **solo** un JSON válido, sin texto adicional.\n\n"
        f"JSON: {json.dumps(json_data, ensure_ascii=False, indent=4)}"
    )
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "Eres un asistente que organiza JSON de manera lógica. Siempre devuelves un JSON válido, sin texto adicional."},
            {"role": "user", "content": prompt}
        ]
    )
    
    structured_json = response.choices[0].message.content
    print("Raw response from API:", structured_json)  # Debugging: Print the raw response
    
    try:
        return json.loads(structured_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("Invalid JSON returned by API:", structured_json)
        return None  # Return None or the original JSON if parsing fails

# Procesar todos los archivos JSON en la carpeta de entrada
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"Procesando {filename}...")
        
        try:
            with open(input_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filename}. Skipping this file.")
            continue
        
        structured_data = restructure_json_with_openai(data)
        
        if structured_data:  # Only save if the structured data is valid
            with open(output_path, "w", encoding="utf-8") as outfile:
                json.dump(structured_data, outfile, indent=4, ensure_ascii=False)
            
            print(f"Guardado en {output_path}")

print("✅ Procesamiento completado.")