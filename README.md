
# Orquestación de Agentes con Arquitectura ReAct

Este repositorio contiene el material práctico desarrollado durante el curso de optimización y orquestación de agentes utilizando **LangGraph**, **LangChain** y LLMs de código abierto.

---

## 📚 Estructura del Aprendizaje

### 🔹 Clase 02: Componentes Esenciales de LangGraph 🚀 *(Rama Actual)*
En esta sección profundizamos en la anatomía interna de un grafo de ejecución para agentes complejos.
* **Grafo Dirigido Acíclico (DAG)**: Modelado del flujo de control del agente mediante nodos y bordes.
* **Nodos (Nodes)**: Unidades de ejecución lógica (funciones de Python) que representan los pasos de pensamiento del LLM o la ejecución de herramientas.
* **Bordes (Edges)**: Reglas de transición. Implementación de **Bordes Condicionales** para decidir dinámicamente el siguiente paso basándose en el estado actual.
* **Manejo del Estado (State)**: Flujo de información centralizado a través del stream del grafo (`abot.graph.stream`).
* **Extracción Dinámica**: Optimización del código para capturar el último nodo ejecutado de forma segura, evitando errores de sobrescritura de claves fijas.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.11+**
* **LangGraph** (Orquestación basada en grafos)
* **LangChain Core** (`HumanMessage`, `SystemMessage`)
* **Groq Cloud API** (Inferencia de ultra alta velocidad utilizando `llama-3.3-70b-versatile`)
* **Tavily API** (Motor de búsqueda optimizado para agentes AI)

---

## 🚀 Cómo ejecutar el proyecto de la Clase 2

1. Asegúrate de estar en la rama correcta:
```bash
   git checkout clase-02
```
   

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/orquestacion-agentes-multiagentes/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/orquestacion-agentes-multiagentes) - Backend Developer.