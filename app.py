import streamlit as st
from agent import agent
import nest_asyncio

# Aplicar patch para bucles de eventos anidados (necesario si Agno usa async internamente)
nest_asyncio.apply()

st.set_page_config(
    page_title="Nexus AI",
    page_icon="🤖",
    layout="wide"
)

# Título y Descripción
st.title("🤖 Nexus - Analista de Investigación")
st.markdown("""
Bienvenido a la interfaz web de **Nexus**. 
Este agente tiene acceso a **Internet**, **Archivos Locales**, **Datos Financieros** y **YouTube**.
""")

# Inicializar historial de chat en session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input de usuario
if prompt := st.chat_input("¿Qué deseas investigar hoy?"):
    # Agregar mensaje de usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Usar el agente para generar respuesta (capturando el stream si es posible, o respuesta completa)
        try:
            # Opción 1: Ejecución estándar obteniendo respuesta directa
            # run_response = agent.run(prompt)
            # full_response = run_response.content
            
            # Opción 2: Streaming (más amigable)
            # Nota: Agno devuelve un generador en stream=True. 
            # Adaptamos para iterar sobre el generador de respuesta.
            response_generator = agent.run(prompt, stream=True)
            
            for chunk in response_generator:
                # Dependiendo de la estructura del chunk de Agno, extraemos el contenido
                # Ajusta esto si el chunk es un objeto y no string directo
                content = ""
                if hasattr(chunk, "content"):
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk
                
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
            full_response = f"Error: {e}"

    # Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar para herramientas/info
with st.sidebar:
    st.header("Configuración")
    st.info("Modelo: Minimax M2.1")
    st.success("Memoria: Activa (SQLite)")
    
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()
