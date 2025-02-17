import streamlit as st  
import json  
import requests  
from rapidfuzz import fuzz  
from dotenv import load_dotenv  
import os  

# Cargar variables de entorno desde el archivo .env  
load_dotenv(override=True)  

# Verifica que las variables de entorno estén cargadas
print("AZURE_TRANSLATOR_ENDPOINT:", os.getenv("AZURE_TRANSLATOR_ENDPOINT"))
print("AZURE_TRANSLATOR_KEY:", os.getenv("AZURE_TRANSLATOR_KEY"))

# Configurar el endpoint de Azure CLU y Translator usando variables de entorno  
AZURE_CLU_ENDPOINT = os.getenv("AZURE_CLU_ENDPOINT")  
AZURE_CLU_KEY = os.getenv("AZURE_CLU_KEY")  
AZURE_TRANSLATOR_ENDPOINT = os.getenv("AZURE_TRANSLATOR_ENDPOINT")  
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")  
PROJECT_NAME = os.getenv("PROJECT_NAME")  
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")  

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

def detectar_intent_y_entidades(texto):  
    """Consulta Azure CLU para obtener intent y entidades."""  
    url = f"{AZURE_CLU_ENDPOINT}/language/:analyze-conversations?api-version=2022-10-01-preview"  
    headers = {"Ocp-Apim-Subscription-Key": AZURE_CLU_KEY, "Content-Type": "application/json"}  
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
            "projectName": PROJECT_NAME,  
            "deploymentName": DEPLOYMENT_NAME,  
            "stringIndexType": "TextElement_V8"  
        }  
    }  

    response = requests.post(url, headers=headers, json=body)  
    data = response.json()  

    intent = data["result"]["prediction"]["topIntent"]  
    entidades = {ent["category"]: ent["text"] for ent in data["result"]["prediction"]["entities"]}  

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

def detectar_idioma(texto):  
    """Detecta el idioma del texto usando Azure Translator."""  
    url = f"{AZURE_TRANSLATOR_ENDPOINT}/detect?api-version=3.1"  
    headers = {  
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,  
        "Content-Type": "application/json"  
    }  
    body = [{"text": texto}]  

    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    print("Respuesta de Azure Translator:", data)  # Agregar esta línea para depuración
    return data[0]["language"]

def traducir_texto(texto, idioma_destino):  
    """Traduce el texto al idioma especificado usando Azure Translator."""  
    url = f"{AZURE_TRANSLATOR_ENDPOINT}/translate?api-version=3.1&to={idioma_destino}"  
    headers = {  
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,  
        "Content-Type": "application/json"  
    }  
    body = [{"text": texto}]  

    response = requests.post(url, headers=headers, json=body)  
    data = response.json()  
    return data[0]["translations"][0]["text"]  

# Interfaz en Streamlit  
st.title("Chatbot de Ordenadores 💻")  
user_input = st.text_input("¿Qué ordenador necesitas?")  

if user_input:  
    # Detectar el idioma del usuario  
    idioma_usuario = detectar_idioma(user_input)  

    # Obtener intent y entidades  
    intent, entidades = detectar_intent_y_entidades(user_input)  
    if intent in ["RealizarPedido", "SolicitarInfo"]:  
        resultado = buscar_ordenador(entidades, json_data)  

        if resultado:  
            # Formatear la respuesta en texto, solo mostrando campos no vacíos  
            respuesta_texto = "### Ordenador recomendado:\n"  
            for clave, valor in resultado.items():  
                if isinstance(valor, dict):  
                    # Para campos que son diccionarios, mostrar sus subcampos no vacíos  
                    sub_respuesta = []  
                    for subclave, subvalor in valor.items():  
                        if subvalor:  # Solo agregar si el valor no está vacío  
                            sub_respuesta.append(f"\n\n- **{subclave}:** {subvalor}")  
                    if sub_respuesta:  # Solo agregar si hay subcampos no vacíos  
                        respuesta_texto += f"**{clave}:**\n" + "\n".join(sub_respuesta) + "\n\n"  
                elif valor:  # Para campos que no son diccionarios  
                    respuesta_texto += f"**{clave}:** {valor}\n\n"  

            # Traducir la respuesta al idioma del usuario  
            respuesta_traducida = traducir_texto(respuesta_texto, idioma_usuario)  
            st.write(respuesta_traducida)  
        else:  
            st.write(traducir_texto("No se encontró un ordenador que coincida con tu solicitud.", idioma_usuario))  
    else:  
        st.write(traducir_texto("No entiendo tu solicitud. ¿Puedes reformularla?", idioma_usuario))  