import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json

# Cargar las variables de entorno desde el archivo .env
load_dotenv(override=True)

# Configura tu endpoint y clave de API desde las variables de entorno
endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY")

client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))

# Ruta al archivo PDF
pdf_path = "fichas-pdf/FMDDY.pdf"

# Procesar el PDF usando el modelo preentrenado
with open(pdf_path, "rb") as pdf_file:
    poller = client.begin_analyze_document("prebuilt-read", document=pdf_file)
    result = poller.result()

# Extraer el texto y estructuras
texto_extraido = []
for page in result.pages:
    for line in page.lines:
        texto_extraido.append(line.content)

# Crear un JSON con el texto extraído
json_resultado = json.dumps({"texto_extraido": texto_extraido}, indent=4)

# Guardar el JSON en un archivo
with open("fichas-txt/resultado.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_resultado)
