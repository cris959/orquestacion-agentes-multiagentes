import os
import gradio as gr
from dotenv import load_dotenv

# Importamos el grafo ya configurado y compilado de tu backend
from new_backend import graph

# Cargamos variables de entorno por seguridad
load_dotenv()

def ejecutar_orquestador(tarea, max_revisiones):
    """
    Función que conecta la interfaz de Gradio con el flujo de agentes de LangGraph.
    """
    if not tarea.strip():
        return "⚠️ Por favor, ingresa una tarea o tema válido."
        
    # 1. Configuración del hilo (Id único para evitar colisiones de memoria)
    # Usamos un ID dinámico por sesión para que cada clic en "Enviar" sea un flujo limpio
    config = {"configurable": {"thread_id": f"gradio_session_{os.getpid()}"}}
    
    # 2. Definimos el estado inicial usando las variables del formulario
    inputs = {
        "task": tarea,
        "max_revisions": int(max_revisiones),
        "revision_number": 1,
        "content": []
    }
    
    # 3. Contenedores para capturar el progreso visual
    logs_progreso = ""
    borrador_final = ""
    
    print(f"\n🖥️ [Gradio UI] Iniciando proceso para la tarea: '{tarea}'")
    
    # 4. Consumimos el stream del grafo paso a paso
    # Como Gradio necesita retornar al final, acumulamos los eventos del ciclo
    for event in graph.stream(inputs, config=config):
        for node_name, output in event.items():
            nombre_nodo = node_name.upper()
            logs_progreso += f"✔️ Nodo Finalizado: [{nombre_nodo}]\n"
            
            # Si el nodo es 'generate', capturamos el borrador para mostrarlo
            if "draft" in output and output["draft"]:
                borrador_final = output["draft"]
                
            # Si el nodo es 'reflect', podemos avisar que el profesor dejó una crítica
            if "critique" in output and output["critique"]:
                logs_progreso += f"   💬 El profesor aplicó una revisión (Intento {output.get('revision_number', 1)-1})\n"
                
    # Si por alguna razón el flujo terminó pero no se generó un borrador largo
    if not borrador_final:
        borrador_final = "No se logró consolidar el borrador final. Revisa los logs de consola."

    return logs_progreso, borrador_final

# ==========================================
# 🎨 DISEÑO DE INTERFAZ DE GRADIO (UI)
# ==========================================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        """
        # 🤖 Orquestador Multi-Agente Cíclico (Clon Alura)
        Ingresa un tema de investigación. El **Planner** armará el esquema, **Tavily** buscará en la web, 
        el **Escritor** redactará y el **Profesor** criticará el borrador en bucle hasta lograr la máxima calidad.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            # Inputs del usuario
            txt_tarea = gr.Textbox(
                label="Tarea / Tema de Investigación", 
                placeholder="Ej: Cuál es la diferencia entre LangChain y LangSmith",
                lines=3
            )
            slider_revisions = gr.Slider(
                minimum=1, 
                maximum=4, 
                value=2, 
                step=1, 
                label="Límite Máximo de Revisiones (Bucle)"
            )
            btn_enviar = gr.Button("🚀 Lanzar Flujo de Agentes", variant="primary")
            
            # Monitor de estado/logs rápidos
            txt_logs = gr.TextArea(
                label="Progreso del Pipeline (Pasos del Grafo)", 
                interactive=False,
                lines=6
            )

        with gr.Column(scale=2):
            # Output final renderizado en Markdown real
            html_resultado = gr.Markdown(
                label="📄 Artículo Final Generado"
            )
            
    # Conectamos el botón con nuestra función del Grafo
    btn_enviar.click(
        fn=ejecutar_orquestador,
        inputs=[txt_tarea, slider_revisions],
        outputs=[txt_logs, html_resultado]
    )

# Lanzamos la aplicación local
if __name__ == "__main__":
    # share=True creará un enlace público temporal por si querés probarlo en el celu
    demo.launch(share=False)