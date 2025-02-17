import os  
import json  
import requests  
from rapidfuzz import fuzz  
from dotenv import load_dotenv  
from openai import AzureOpenAI  
  
# Cargar variables de entorno desde el archivo .env  
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
  
# Ruta de la carpeta que contiene los archivos JSON  
RUTA_JSON = "fichas-json-clean-structured/"  
  
# Cargar todos los archivos JSON de la carpeta  
def cargar_json_desde_carpeta(ruta):  
    """Carga todos los archivos JSON de una carpeta en una lista."""  
    json_data = []  
    for archivo in os.listdir(ruta):  
        if archivo.endswith(".json"):  
            with open(os.path.join(ruta, archivo), "r", encoding="utf-8") as f:  
                json_data.append(json.load(f))  
    return json_data  
  
# Cargar todos los JSON  
json_data = cargar_json_desde_carpeta(RUTA_JSON)  
  
def detectar_idioma(texto):  
    """Usa GPT-4 para detectar el idioma del texto."""  
    response = client.chat.completions.create(  
        model=DEPLOYMENT_NAME,  
        messages=[  
            {"role": "user", "content": f"Detecta el idioma del siguiente texto: '{texto}'. Solo devuelve el nombre del idioma."}  
        ],  
        max_tokens=10,  
        temperature=0  
    )  
    return response.choices[0].message.content.strip()  
  
def detectar_intent_y_entidades(texto):  
    """Consulta Azure CLU para obtener intent y entidades."""  
    url = f"{OPENAI_ENDPOINT}/language/:analyze-conversations?api-version=2022-10-01-preview"  
    headers = {  
        "Ocp-Apim-Subscription-Key": os.getenv("AZURE_CLU_KEY"),  
        "Content-Type": "application/json"  
    }  
    body = {  
        "kind": "Conversation",  
        "analysisInput": {  
            "conversationItem": {  
                "text": texto,  
                "id": "1",  
                "participantId": "user"  
            }  
        },  
        "parameters": {  
            "projectName": os.getenv("PROJECT_NAME"),  
            "deploymentName": os.getenv("DEPLOYMENT_NAME"),  
            "stringIndexType": "TextElement_V8"  
        }  
    }  
  
    response = requests.post(url, headers=headers, json=body)  
  
    # Manejo de errores  
    if response.status_code != 200:  
        st.error(f"Error en la solicitud: {response.status_code} - {response.text}")  
        return None, None  
  
    data = response.json()  
  
    # Verificar si la respuesta tiene la estructura esperada  
    if "result" not in data or "prediction" not in data["result"]:  
        st.error(f"La respuesta no contiene 'result' o 'prediction': {data}")  
        return None, None  
  
    # Asegúrate de que la clave 'topIntent' existe  
    if "topIntent" not in data["result"]["prediction"]:  
        st.error(f"No se encontró 'topIntent' en la respuesta: {data}")  
        return None, None  
  
    intent = data["result"]["prediction"]["topIntent"]  
    entidades = {ent["category"]: ent["text"] for ent in data["result"]["prediction"].get("entities", [])}  
  
    return intent, entidades  

def buscar_ordenador(similitudes, json_data):  
    """Encuentra el ordenador más similar usando RapidFuzz."""  
    mejor_match = None  
    mejor_puntaje = 0  
  
    for data in json_data:  # Iterar sobre cada archivo JSON cargado  
        for ordenador in data.get("Productos", []):  # Asumimos que cada JSON tiene una clave "Productos"  
            puntaje_total = 0  
            num_caracteristicas = 0  
  
            for entidad, valor_usuario in similitudes.items():  
                valor_json = ordenador.get(entidad, "")  
                if isinstance(valor_json, dict):  
                    valor_json = " ".join(valor_json.values())  
  
                score = fuzz.partial_ratio(valor_usuario.lower(), valor_json.lower())  
                puntaje_total += score  
                num_caracteristicas += 1  
  
            promedio = puntaje_total / num_caracteristicas if num_caracteristicas else 0  
            if promedio > mejor_puntaje:  
                mejor_puntaje = promedio  
                mejor_match = ordenador  
  
    return mejor_match  
  
def obtener_recomendacion_gpt4(user_input, intent, entidades, idioma):  
    """Usa GPT-4 para obtener una recomendación basada en el input del usuario, intents y entidades."""  
    prompt = f"El usuario ha dicho: '{user_input}'. El intent detectado es '{intent}' y las entidades son {entidades}. Basado en esta información, recomienda el producto más adecuado de los archivos JSON en la carpeta 'fichas-json-clean-structured/'. Responde en el idioma '{idioma}'."  
  
    response = client.chat.completions.create(  
        model=DEPLOYMENT_NAME,  
        messages=[  
            {"role": "user", "content": prompt}  
        ],  
        max_tokens=150,  
        temperature=0.7  
    )  
  
    return response.choices[0].message.content.strip()  
  
# Interfaz en Streamlit  
import streamlit as st  
  
st.title("Chatbot de Ordenadores 💻")  
user_input = st.text_input("¿Qué ordenador necesitas?")  
  
if user_input:  
    # Detectar idioma  
    idioma = detectar_idioma(user_input)  
    st.write(f"Idioma detectado: {idioma}")  
  
    # Detectar intents y entidades  
    intent, entidades = detectar_intent_y_entidades(user_input)  
    st.write(f"Intent detectado: {intent}")  
    st.write(f"Entidades detectadas: {entidades}")  
  
    # Obtener recomendación de GPT-4  
    recomendacion = obtener_recomendacion_gpt4(user_input, intent, entidades, idioma)  
    st.write("### Recomendación basada en GPT-4:")  
    st.write(recomendacion)  
  
    # Buscar el ordenador más similar  
    if intent in ["RealizarPedido", "SolicitarInfo"]:  
        resultado = buscar_ordenador(entidades, json_data)  
        st.write("### Ordenador recomendado:")  
        st.json(resultado)  
    else:  
        st.write("No entiendo tu solicitud. ¿Puedes reformularla?")  
