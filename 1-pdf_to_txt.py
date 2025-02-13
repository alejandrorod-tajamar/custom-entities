import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Cargar las variables de entorno desde el archivo .env
load_dotenv(override=True)

# Configura tu endpoint y clave de API desde las variables de entorno
endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY")

# Cliente de Azure Document Intelligence
client = DocumentAnalysisClient(endpoint, AzureKeyCredential(api_key))

# Rutas de las carpetas
ruta_pdf = "fichas-pdf/"
ruta_txt = "fichas-txt/"

# Asegurar que la carpeta de salida existe
os.makedirs(ruta_txt, exist_ok=True)

# Procesar cada PDF en la carpeta
for archivo in os.listdir(ruta_pdf):
    if archivo.endswith(".pdf"):
        pdf_path = os.path.join(ruta_pdf, archivo)
        txt_path = os.path.join(ruta_txt, archivo.replace(".pdf", ".txt"))

        with open(pdf_path, "rb") as pdf_file:
            poller = client.begin_analyze_document("prebuilt-read", document=pdf_file)
            result = poller.result()

        # Extraer texto
        texto_extraido = "\n".join([line.content for page in result.pages for line in page.lines])

        # Guardar el texto en un archivo
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(texto_extraido)

        print(f"Procesado: {archivo} → Guardado en {txt_path}")

print("✅ Todos los PDFs han sido procesados y guardados en fichas-txt/")
