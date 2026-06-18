import os
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv

# Importaciones oficiales de LangChain / LangGraph
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# ==========================================
# 0. CONFIGURACIÓN DE ENTORNO Y LLAMADAS
# ==========================================
load_dotenv()

if not os.environ.get("GROQ_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
    print("⚠️ ¡Atención! Verifica tu archivo .env, faltan las API Keys de Groq o Tavily.")

# Inicializamos el LLM (Llama 3.3) y la herramienta de búsqueda de Alura
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
search_tool = TavilySearchResults(max_results=2)

# ==========================================
# 1. DEFINICIÓN DEL ESTADO (AgentState)
# ==========================================
class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    revision_number: int
    max_revisions: int
    content: List[str]

# ==========================================
# 2. DEFINICIÓN DE NODOS CON PROMPTS REALES
# ==========================================

def plan_node(state: AgentState):
    print("\n🧠 [Nodo: Planner] Creando la estructura del artículo...")
    
    system_prompt = (
        "Eres un director de contenido experto. Tu trabajo es segmentar una tarea de investigación "
        "en un esquema o índice detallado paso a paso. Sé claro, profesional y organiza la información "
        "estructurándola con títulos y subtítulos en Markdown."
    )
    user_prompt = f"Genera el esquema ideal para la siguiente tarea: '{state['task']}'."
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)
    return {"plan": response.content}


def research_plan_node(state: AgentState):
    print("🔍 [Nodo: Research Plan] Investigando en internet los puntos del plan...")
    
    # Creamos una query optimizada combinando la tarea y el inicio del plan
    query = f"{state['task']} analisis tecnico diferencias"
    search_results = search_tool.invoke({"query": query})
    
    # Extraemos el contenido de los resultados devueltos por Tavily
    fetched_info = []
    for result in search_results:
        if isinstance(result, dict) and "content" in result:
            fetched_info.append(result["content"])
            
    joined_info = "\n--- Resultado de Búsqueda ---\n".join(fetched_info)
    return {"content": [joined_info]}


def generation_node(state: AgentState):
    print(f"✍️ [Nodo: Generate] Redactando borrador técnico (Revisión Nro {state.get('revision_number', 1)})...")
    
    system_prompt = (
        "Eres un escritor técnico de primer nivel especializado en Inteligencia Artificial y Software. "
        "Tu objetivo es redactar un artículo completo, fluido, profundo y enriquecido en formato Markdown. "
        "Usa el plan provisto y la información recopilada de internet. Si recibes una crítica de un profesor, "
        "corrige y expande los puntos débiles que te marcó sin justificarte, solo entrega el texto mejorado."
    )
    
    # Consolidamos toda la información de contexto que tenemos en el estado
    investigaciones = "\n\n".join(state.get("content", []))
    critica_previa = state.get("critique", "Ninguna. Es tu primer borrador.")
    
    user_prompt = (
        f"• TAREA PRINCIPAL: {state['task']}\n"
        f"• ESQUEMA A SEGUIR:\n{state['plan']}\n\n"
        f"• INFORMACIÓN DISPONIBLE (CONTESTO):\n{investigaciones}\n\n"
        f"• CRÍTICA DEL PROFESOR A CORREGIR:\n{critica_previa}\n\n"
        f"Por favor, genera o reescribe el artículo completo ahora."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)
    return {"draft": response.content}


def reflection_node(state: AgentState):
    print("🎓 [Nodo: Reflect] El profesor está evaluando el borrador actual...")
    
    system_prompt = (
        "Eres un profesor universitario de informática sumamente estricto y exigente. "
        "Tu trabajo es revisar el borrador del alumno. Busca errores conceptuales, falta de profundidad, "
        "ausencia de ejemplos claros o explicaciones superficiales. "
        "Devuelve una crítica constructiva pero rigurosa detallando exactamente qué debe mejorar el alumno."
    )
    
    user_prompt = (
        f"Evalúa críticamente este borrador escrito por el alumno:\n\n{state['draft']}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = llm.invoke(messages)
    
    # Incrementamos el contador de revisiones
    current_rev = state.get("revision_number", 1)
    return {
        "critique": response.content,
        "revision_number": current_rev + 1
    }


def research_critique_node(state: AgentState):
    print("🔬 [Nodo: Research Critique] Investigando soluciones en la web para resolver la crítica...")
    
    # Tomamos un fragmento clave de la crítica para buscar datos específicos en internet
    critica_texto = state.get("critique", "")
    query_critica = f"detalles avanzados sobre {critica_texto[:80]}"
    
    search_results = search_tool.invoke({"query": query_critica})
    
    fetched_info = []
    for result in search_results:
        if isinstance(result, dict) and "content" in result:
            fetched_info.append(result["content"])
            
    joined_info = f"\n--- Datos para resolver la crítica ---\n" + "\n".join(fetched_info)
    
    # Agregamos los nuevos datos al historial de contenido existente sin pisar lo anterior
    lista_actual = state.get("content", [])
    return {"content": lista_actual + [joined_info]}

# ==========================================
# 3. LÓGICA DE CONTROL (Bifurcación Condicional)
# ==========================================
def should_continue(state: AgentState):
    current_revision = state.get("revision_number", 1)
    max_allowed = state.get("max_revisions", 2)
    
    if current_revision > max_allowed:
        print(f"\n🛑 [Condicional] Límite de {max_allowed} revisiones alcanzado. Cortando flujo y enviando borrador final.")
        return END
        
    print(f"\n🔄 [Condicional] Revisión actual: {current_revision} de {max_allowed}. Enviando a evaluación en 'reflect'.")
    return "reflect"

# ==========================================
# 4. ENSAMBLADO DEL GRAFO (Clon Estructura Alura)
# ==========================================
builder = StateGraph(AgentState)

# Registro de Nodos
builder.add_node("planner", plan_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("generate", generation_node)  
builder.add_node("reflect", reflection_node)
builder.add_node("research_critique", research_critique_node)

# Flujo lineal de entrada
builder.add_edge(START, "planner")
builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")

# Lógica condicional saliendo de 'generate' hacia el ciclo o el final
builder.add_conditional_edges(
    "generate",
    should_continue,
    {
        "reflect": "reflect",
        END: END
    }
)

# Retorno del bucle recurrente
builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")

# Inicialización de Persistencia
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# ==========================================
# 5. BLOQUE DE EJECUCIÓN SCRIPT (.py)
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 SERVIDOR DE AGENTES LANGGRAPH ACTIVO (CLASE 06)")
    print("="*60 + "\n")
    
    # ID de hilo único para pruebas en producción limpia
    config = {"configurable": {"thread_id": "hilo_produccion_completo"}}
    
    inputs = {
        "task": "Cuál es la diferencia entre LangChain y LangSmith",
        "max_revisions": 2,  # Configurado para dar 2 vueltas completas de mejora
        "revision_number": 1,
        "content": []
    }
    
    print("🚀 Iniciando ejecución en streaming...")
    
    for event in graph.stream(inputs, config=config):
        for node_name, output in event.items():
            print(f"\n📦 【 NODO FINALIZADO: {node_name.upper()} 】")
            for key, value in output.items():
                texto_str = str(value)
                # Si el artículo o crítica es gigante, mostramos los primeros 400 caracteres en consola
                if len(texto_str) > 400:
                    texto_str = texto_str[:400] + "\n... [Texto truncado en consola por legibilidad] ..."
                print(f"🔹 {key}: {texto_str}")
        print("\n" + "-" * 60)