
# 🤖 Orquestación de Agentes con Arquitectura ReAct

Este proyecto implementa un agente inteligente utilizando el patrón de diseño **ReAct** (Reasoning and Acting) para la gestión e interacción interactiva con un sistema de inventario simulado. 

Originalmente desarrollado sobre el ecosistema de Google Gemini, el backend fue migrado estratégicamente hacia **Groq (Llama 3.3)** para optimizar la velocidad de respuesta y evadir las estrictas limitaciones de cuota (*Rate Limits*) por IP.

---

## 🧭 ¿Qué es la Arquitectura ReAct?

El patrón ReAct combina la capacidad de los Modelos de Lenguaje (LLMs) para generar trazas de razonamiento (*Reasoning*) junto con la ejecución de acciones específicas basadas en herramientas (*Acting*). El agente sigue un bucle continuo de tres pasos:

1. **Pensamiento (Thought):** El modelo analiza la entrada y decide qué necesita saber o hacer.
2. **Acción (Action):** El modelo invoca una herramienta externa (ej. `consultar_stock`, `calcular_precio`).
3. **Observación (Observation):** El sistema ejecuta el código en Python, le devuelve el resultado real al modelo, y este decide si ya puede dar la respuesta final o si necesita usar otra herramienta.

---

## ⚡ El Desafío Técnico: De Gemini a Groq

### 1. El Problema (Google Gemini)
Durante las pruebas con el modelo `gemini-2.5-flash`, el ciclo continuo de llamadas rápidas que requiere el bucle ReAct colapsó la cuota gratuita de la API de Google por minuto. Esto generaba errores de tipo `ResourceExhausted (429)` y bloqueos de IP prolongados (con penalizaciones de reintento de casi un minuto por interacción), rompiendo la experiencia interactiva por consola.

### 2. La Solución (Groq + Llama 3.3 70B)
Para resolver la asfixia de la cuota, migramos el motor del agente al cliente de **Groq**, utilizando el modelo **`llama-3.3-70b-versatile`**. 
* **Ventajas:** Procesamiento en milisegundos, latencia ultra baja y límites de cuota por minuto drásticamente más amplios para entornos de desarrollo.
* **Control de Alucinaciones:** Se implementó el parámetro de parada `stop=["PAUSA", "Observación:"]` en la API de Groq para forzar al modelo a congelar su generación de texto inmediatamente después de declarar una acción. Esto evita que el LLM "invente" las respuestas de las herramientas y garantiza que Python tome el control de la lógica de negocio.

---

## 🛠️ Herramientas Disponibles del Agente

El agente tiene acceso a un kit de herramientas escritas en Python para interactuar con el inventario en tiempo real:
* `consultar_stock(producto)`: Devuelve las unidades disponibles.
* `consultar_precio_producto(producto)`: Devuelve el costo unitario en USD.
* `encontrar_producto_mas_costoso()`: Identifica el ítem de mayor valor.
* `calcular_valor_total_lista(lista)`: Suma los precios de múltiples artículos de forma masiva.

---

## 🚀 Configuración del Proyecto

### Requisitos Previos
Tener instalado Python 3.10+ y un entorno virtual configurado.

### Instalación de Dependencias
```bash
pip install groq python-dotenv
```

### 🔑 Gestión de Credenciales y Seguridad
La arquitectura de este proyecto sigue estrictamente las buenas prácticas de desarrollo (12-Factor App) para el manejo de información sensible, separando la lógica de negocio de las credenciales de acceso.

1. El archivo .env (Variables de Envío / Entorno)
En lugar de "hardcodear" (escribir directamente) las llaves privadas en el código de Python, las credenciales se almacenan localmente en un archivo de configuración llamado .env en la raíz del proyecto. El SDK de los diferentes proveedores y herramientas (como LangGraph o Tavily) están diseñados para buscar de forma nativa e automática estas variables en el entorno del sistema.

## Estructura requerida y actualizada del archivo .env:

```
# Configuración de Proveedores de LLM
GEMINI_API_KEY=AIzaSyYourGeminiKeyHere
GROQ_API_KEY=gsk_YourGroqSecretKeyHere

# Herramientas de Búsqueda Avanzada para Agentes (Web Search)
TAVILY_API_KEY=tvly-YourTavilyKeyHere
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/orquestacion-agentes-multiagentes/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/orquestacion-agentes-multiagentes) - Backend Developer.