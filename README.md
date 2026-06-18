
## 📬 Sistema Multi-Agente de Triaje y Respuesta de Emails con LangGraph

Este repositorio contiene el desarrollo práctico de la **Clase 07: Creando un Asistente de Email**. El objetivo del proyecto es construir un sistema de orquestación multi-agente capaz de recibir correos entrantes, clasificarlos según reglas de negocio corporativas y delegar la redacción técnica de las respuestas a un agente ReAct motorizado por **Groq (Llama 3.3)**.

## 🛠️ Tecnologías Utilizadas
* **Python 3.14** (Entorno Virtual `.venv`)
* **LangGraph & LangChain** (Orquestación de grafos de estado y agentes ReAct)
* **Pydantic v2** (Garantía de salida estructurada)
* **Groq API** (`llama-3.3-70b-versatile` para inferencia de alta velocidad y baja latencia)

---

## 🚀 Arquitectura del Grafo

El flujo de control se gestiona mediante un `StateGraph` que utiliza un estado compartido (`State`) basado en `TypedDict` para almacenar el diccionario del email entrante (`email_input`) y el historial de conversación (`messages`).

1. **`START`** ➡️ El flujo inicia enviando el input al nodo de triaje.
2. **`triage_router`** ➡️ Clasifica el correo. Si el resultado es `"respond"`, actualiza el estado inyectando el comando y desvía el flujo al agente. Si es `"ignore"` o `"notify"`, el flujo finaliza en el nodo especial `__end__`.
3. **`response_agent`** ➡️ Agente ReAct encargado de generar la respuesta corporativa final utilizando el contexto heredado.

---

## 🧠 Desafíos Técnicos Resueltos y Aprendizajes Clave

Durante el desarrollo de esta clase, nos enfrentamos a varios desafíos críticos de arquitectura en sistemas multi-agente:

### 1. Control de Loops Infinitos en Agentes ReAct (`recursion_limit`)
* **Problema:** Al procesar correos que requerían una respuesta compleja (como el caso de prueba de Alice consultando por endpoints de la API), el agente de respuesta entraba en un bucle infinito (*loop*) intentando razonar o buscar herramientas inexistentes, consumiendo cuotas de la API de Groq sin detenerse.
* **Solución:** Se implementó un freno de mano de seguridad inyectando un límite de recursión en la configuración del `.invoke()`:
  
  ```
  python
  
  configuracion = {"recursion_limit": 10}
  response = app.invoke({"email_input": email_input}, config=configuracion)
  ```
Esto garantiza que el grafo se interrumpa de forma segura si realiza más de 10 saltos entre nodos.

2. Error de Atributo en AIMessage (**'AIMessage' object has no attribute 'classification'**)
* Problema: El LLM en el enrutador (**llm_router.invoke**) devolvía texto plano envuelto en un objeto **AIMessage**, rompiendo la validación condicional **result.classification == "respond"** ya que las propiedades personalizadas no existen de forma nativa en los mensajes de chat.

* Solución: Implementamos salida estructurada forzada combinando un esquema de Pydantic con el método **.with_structured_output()** de LangChain:

```
Python

from pydantic import BaseModel, Field

class TriageOutput(BaseModel):
    classification: Literal["respond", "ignore", "notify"] = Field(...)

llm_router = llm_base.with_structured_output(TriageOutput)
```
Esto obligó al modelo Llama 3.3 a responder con un JSON estricto que Python parsea nativamente con la propiedad requerida.

3. Actualización de Sintaxis en LangGraph (**state_modifier** vs **prompt**)
* Problema: El constructor preconstruido de agentes **create_react_agent** arrojaba un **TypeError** al intentar pasarle las instrucciones del sistema mediante la propiedad obsoleta **state_modifier**.

* Solución: Se migró la sintaxis a los estándares actuales de LangGraph, reemplazando el argumento por **prompt**:

```
Python

agent = create_react_agent(model=llm, tools=[], prompt="Sos un asistente corporativo experto...")
```
4. Rehidratación de Memoria tras Reinicios de Kernel
* Problema: Al interrumpir o reiniciar el Kernel de Jupyter para frenar los bucles infinitos, la memoria dinámica se limpiaba por completo provocando errores en cascada de tipo **NameError** (**State is not defined, triage_router is not defined, app is not defined**).

* Solución: Se diseñó un script de inicialización acoplado y centralizado en una única celda que declara contratos de tipado, inicializa modelos, compila el grafo e inyecta los mocks de datos (**email_input, profile, prompt_instructions**) de un solo tirón, garantizando idempotencia en el entorno de desarrollo.

5. Formateo y Visualización de Trazas (**pretty_print**)
* Problema: El print tradicional del último mensaje ocultaba el flujo interno de LangGraph y los metadatos de las interacciones.

* Solución: Se implementó el bucle iterativo nativo de LangChain para renderizar de manera estética el ciclo de vida del estado en la consola:
```
Python

for m in response["messages"]:
    m.pretty_print()
```
Esto permitió contrastar visualmente cómo un agente con herramientas (**tools=[write_email]**) genera un mensaje con metadatos de **Tool Calls** y **Call ID**, a diferencia de un agente sin herramientas integradas (**tools=[]**) que responde con texto plano directo en el atributo **content**.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/orquestacion-agentes-multiagentes/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/orquestacion-agentes-multiagentes) - Backend Developer.