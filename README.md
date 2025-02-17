# Custom Entities Project

## Uso de la aplicación

- Acceder al enlace: []()
- Utilizar las [preguntas de ejemplo](example-inputs.md) como guía para probar el chatbot.
- Escribir mensajes propios en el chat que sean similares a los de ejemplo para comprobar cuáles funcionan mejor.
- Para ver la intención y las entidades detectadas en cada mensaje mandado, expandir el desplegable de la parte superior del chat.

## [OPCIONAL] Instalación en local

Clona este proyecto:

```bash
git clone https://github.com/alejandrorod-tajamar/custom-entities.git
```

Navega hasta la carpeta del proyecto:

```cmd
cd custom-entities
```

Crea un entorno virtual:

```cmd
py -m venv .venv
```

Activa el entorno virtual:

```cmd
.venv\Scripts\activate
```

Instala las dependencias del proyecto:

```cmd
pip install -r requirements.txt
```

Crea un archivo `.env`, con la siguiente estructura:

```ini
# Document Intelligence
AZURE_ENDPOINT=
AZURE_API_KEY=

# Storage Blob Account
AZURE_STORAGE_CONNECTION_STRING=

# OpenAI API
OPENAI_API_KEY=
OPENAI_ENDPOINT=
OPENAI_API_VERSION=

# Custom Language Understanding
AZURE_CLU_ENDPOINT=
AZURE_CLU_KEY=
PROJECT_NAME=
DEPLOYMENT_NAME=

# Translator
AZURE_TRANSLATOR_ENDPOINT=
AZURE_TRANSLATOR_KEY=
```

Por último, utiliza la última sección de código en [app_v5.py](/app_v5.py) para hacer pruebas y editar el input que le quieras mandar a tu app. Para ejecutarla, utiliza:

```cmd
py app_v5.py
```
