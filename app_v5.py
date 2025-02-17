import streamlit as st  
import json  
import requests  
from rapidfuzz import fuzz  
from dotenv import load_dotenv  
import os  

# Cargar variables de entorno desde el archivo .env  
load_dotenv(override=True)  

# Configurar endpoints y claves
AZURE_CLU_ENDPOINT = os.getenv("AZURE_CLU_ENDPOINT")  
AZURE_CLU_KEY = os.getenv("AZURE_CLU_KEY")  
PROJECT_NAME = os.getenv("PROJECT_NAME")  
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")  
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  

# Cargar credenciales desde Streamlit Secrets
AZURE_CLU_ENDPOINT = st.secrets["AZURE_CLU_ENDPOINT"]
AZURE_CLU_KEY = st.secrets["AZURE_CLU_KEY"]
PROJECT_NAME = st.secrets["PROJECT_NAME"]
DEPLOYMENT_NAME = st.secrets["DEPLOYMENT_NAME"]
OPENAI_ENDPOINT = st.secrets["OPENAI_ENDPOINT"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Cargar datos JSON
RUTA_JSON = "fichas-json-clean-structured/"  

def cargar_json_desde_carpeta(ruta):  
    json_data = []  
    for archivo in os.listdir(ruta):  
        if archivo.endswith(".json"):  
            with open(os.path.join(ruta, archivo), "r", encoding="utf-8") as f:  
                json_data.append(json.load(f))  
    return json_data  

json_data = cargar_json_desde_carpeta(RUTA_JSON)  

# Funciones mejoradas con manejo de errores y modelo chat
def detectar_idioma(texto):
    """Detecta el idioma usando Azure OpenAI Chat Completions"""
    url = f"{OPENAI_ENDPOINT}/openai/deployments/gpt-4o-mini/chat/completions?api-version=2023-12-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": OPENAI_API_KEY
    }
    body = {
        "messages": [
            {"role": "system", "content": "Detecta el idioma del texto y responde solo con el código ISO 639-1."},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.1,
        "max_tokens": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip().lower()
    except Exception as e:
        st.error(f"Error detectando idioma: {str(e)}")
        return "es"  # Idioma por defecto

def traducir_texto(texto, idioma_objetivo):
    """Traduce texto usando Azure OpenAI Chat Completions"""
    if idioma_objetivo == "es":
        return texto
        
    url = f"{OPENAI_ENDPOINT}/openai/deployments/gpt-4o-mini/chat/completions?api-version=2023-12-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": OPENAI_API_KEY
    }
    body = {
        "messages": [
            {"role": "system", "content": f"Traduce este texto al {idioma_objetivo}. Responde solo con la traducción."},
            {"role": "user", "content": texto}
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Error en traducción: {str(e)}")
        return texto

# Resto de funciones actualizadas
def detectar_intent_y_entidades(texto):  
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
    
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        intent = data["result"]["prediction"]["topIntent"]
        entidades = {ent["category"]: ent["text"] for ent in data["result"]["prediction"]["entities"]}
        return intent, entidades
    except Exception as e:
        st.error(f"Error analizando intención: {str(e)}")
        return None, {}

def buscar_ordenador(similitudes, json_data):  
    mejor_match = None  
    mejor_puntaje = 0  

    for data in json_data:  
        for ordenador in data.get("Productos", []):  
            puntaje_total = 0  
            num_caracteristicas = 0  

            for entidad, valor_usuario in similitudes.items():  
                valor_json = ordenador.get(entidad, "")  
                if isinstance(valor_json, dict):  
                    valor_json = " ".join(valor_json.values())  
                  
                score = fuzz.partial_ratio(valor_usuario.lower(), valor_json.lower())  
                puntaje_total += score  
                num_caracteristicas += 1  
              
            if num_caracteristicas > 0:  
                promedio = puntaje_total / num_caracteristicas  
                if promedio > mejor_puntaje:  
                    mejor_puntaje = promedio  
                    mejor_match = ordenador  

    return mejor_match if mejor_puntaje > 70 else None  # Umbral de similitud

# Interfaz Streamlit actualizada
# Usar Markdown con HTML para colorear parte del texto
st.markdown(
    "<h1 style='text-align: center;'>PC RECOMMEND<span style='color: red;'>AI</span>TION 💻</h1>", 
    unsafe_allow_html=True
)

# Inicializar variables para el desplegable
idioma_detectado = "es"
intent_detectado = None
entidades_detectadas = {}

user_input = st.text_input("¿Qué ordenador buscas?")  

if user_input:  
    idioma_detectado = detectar_idioma(user_input)
    texto_traducido = traducir_texto(user_input, "es") if idioma_detectado != "es" else user_input
    
    intent_detectado, entidades_detectadas = detectar_intent_y_entidades(texto_traducido)  
    
    if intent_detectado in ["RealizarPedido", "SolicitarInfo"]:  
        resultado = buscar_ordenador(entidades_detectadas, json_data)  

        if resultado:  
            respuesta = "### Ordenador recomendado:\n"  
            for clave, valor in resultado.items():  
                if isinstance(valor, dict):  
                    sub_respuesta = [f"- **{subclave}:** {subvalor}" for subclave, subvalor in valor.items() if subvalor]
                    if sub_respuesta:  
                        respuesta += f"**{clave}:**\n" + "\n".join(sub_respuesta) + "\n\n"  
                elif valor:  
                    respuesta += f"**{clave}:** {valor}\n\n"  
            
            respuesta_final = traducir_texto(respuesta, idioma_detectado)
            st.markdown(respuesta_final)  
        else:  
            st.write(traducir_texto("No se encontró un ordenador que coincida con tu solicitud.", idioma_detectado))  
    else:  
        st.write(traducir_texto("No entiendo tu solicitud. ¿Puedes reformularla?", idioma_detectado))  

# Mostrar el desplegable con la información detectada
with st.expander("Información detectada"):
    st.write(f"**Idioma detectado:** {idioma_detectado}")
    st.write(f"**Intent detectado:** {intent_detectado}")
    st.write("**Entidades detectadas:**")
    for entidad, valor in entidades_detectadas.items():
        st.write(f"- {entidad}: {valor}")