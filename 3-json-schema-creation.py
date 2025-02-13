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
SCHEMA_PATH = "common_schema.json"  # Ruta para guardar el esquema común

def generate_common_schema(input_dir):
    """Genera un esquema común basado en todos los JSON en la carpeta de entrada."""
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    if not json_files:
        print("No se encontraron archivos JSON en la carpeta de entrada.")
        return None
    
    # Leer todos los JSON y combinarlos en una lista
    combined_data = []
    for filename in json_files:
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as file:
            data = json.load(file)
            combined_data.append(data)
    
    # Crear un prompt para generar un esquema común
    prompt = (
        "Analiza los siguientes JSON y genera un esquema común que pueda organizar todos ellos de manera uniforme. "
        "El esquema debe ser flexible pero consistente, y debe cubrir todas las posibles categorías y campos presentes en los JSON. "
        "Devuelve **solo** un JSON válido que represente el esquema común, sin texto adicional.\n\n"
        f"JSONs: {json.dumps(combined_data, ensure_ascii=False, indent=4)}"
    )
    
    # Enviar el prompt al modelo
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "Eres un asistente que genera esquemas JSON comunes basados en múltiples JSON de entrada."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Obtener y validar el esquema común
    common_schema = response.choices[0].message.content.strip()
    try:
        # Asegurarnos de que el contenido es un JSON válido
        common_schema = json.loads(common_schema)
        print("Esquema común generado con éxito.")
        return common_schema
    except json.JSONDecodeError as e:
        print(f"Error: No se pudo generar un esquema común válido. Detalles: {e}")
        print("Respuesta del modelo:", common_schema)
        return None

# Generar el esquema común
common_schema = generate_common_schema(INPUT_DIR)

# Guardar el esquema común en un archivo
if common_schema:
    with open(SCHEMA_PATH, "w", encoding="utf-8") as schema_file:
        json.dump(common_schema, schema_file, indent=4, ensure_ascii=False)
    print(f"Esquema común guardado en {SCHEMA_PATH}.")
else:
    print("No se pudo generar el esquema común.")