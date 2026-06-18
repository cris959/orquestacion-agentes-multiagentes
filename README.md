

## 🤖 Orquestador Multi-Agente Cíclico con LangGraph y Gradio

Este proyecto implementa un pipeline de orquestación multi-agente cíclico utilizando **LangGraph**, **LangChain** y **Groq (Llama 3.3)**. El sistema simula un flujo de trabajo académico/profesional de investigación y redacción técnica, donde las propuestas y borradores pasan por un proceso de crítica y refinamiento en bucle controlado por variables de estado y persistencia local.

La aplicación incluye una interfaz web interactiva desarrollada con **Gradio** para facilitar las pruebas y la visualización del comportamiento de los agentes en tiempo real.

---

## 🏗️ Arquitectura del Grafo

El flujo sigue la estructura de orquestación analizada en el curso, donde el condicional evalúa el estado del documento saliendo del nodo de generación:

* **Planner**: Diseña el esquema y la estructura inicial en Markdown basados en la tarea del usuario.
* **Research Plan**: Realiza una búsqueda inicial en la web utilizando **Tavily Search** para recopilar contexto técnico fundamental.
* **Generate (Escritor)**: Redacta o mejora el borrador final combinando el plan, la información investigada y las críticas previas.
* **Reflect (Profesor)**: Evalúa rigurosamente el borrador actual generando una crítica constructiva e incrementando el contador de revisiones.
* **Research Critique**: Investiga en internet soluciones específicas orientadas a resolver las observaciones del profesor antes de reescribir.

## 🔄 Flujo de Control (should_continue)
El grafo utiliza un borde condicional (`add_conditional_edges`) que verifica si el número actual de revisiones superó el límite (`max_revisions`). Si quedan intentos, el flujo se redirige a evaluación y optimización; de lo contrario, finaliza de forma segura enviando el borrador con la máxima calidad alcanzada.

---

## 🛠️ Requisitos e Instalación

### 1. Clonar el proyecto y preparar el entorno
````
Bash

# Acceder a la carpeta del proyecto
cd MULTIAGENTES_LANGGRAPH

# Asegúrate de tener tu entorno virtual activo
# En Windows:
.venv\Scripts\activate
````
2. Instalar dependencias necesarias
Asegúrate de contar con los paquetes clave actualizados en tu entorno:
````
Bash

pip install langchain-groq langchain-community langgraph gradio python-dotenv
````
3. Configuración de Variables de Entorno (**.env**)
Crea un archivo .env en la raíz del proyecto (este archivo está protegido en el **.gitignore** y no se subirá al repositorio público) con tus credenciales:
````
Fragmento de código

GROQ_API_KEY="tu_api_key_de_groq_aqui"
TAVILY_API_KEY="tu_api_key_de_tavily_aqui"
````
Nota: El sistema utiliza el modelo **llama-3.3-70b-versatile** en Groq para garantizar la compatibilidad y velocidad en la inferencia de los agentes.

## 🚀 Ejecución de la Aplicación
El proyecto está modularizado para ejecutarse en modo producción (backend aislado) o mediante la interfaz de usuario:

## Interfaz Web (Recomendado)
Para levantar el servidor local de Gradio y probar el orquestador desde tu navegador web:
````
Bash

python app.py
````
Abre en tu navegador la URL local indicada en la terminal (ej. **http://127.0.0.1:7860**).

## Consola / Script Base
Si deseas validar la compilación del grafo y observar el comportamiento de persistencia del **MemorySaver** en la terminal:
````
Bash

python new_backend.py
````
## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/orquestacion-agentes-multiagentes/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/orquestacion-agentes-multiagentes) - Backend Developer.