import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
MAX_FREE_MESSAGES = 5  # Límite de consultas con la API Key del autor

st.set_page_config(page_title="IA de Estudio", layout="wide", page_icon="📚")
st.title("📚 Asistente IA de Estudio: Multi-RAG")

# ---  GESTIÓN DE SEGURIDAD Y API KEYS ---

# Inicializamos el contador de mensajes en la sesión si no existe
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# Obtenemos la api-key para la demo desde el entorno virtual (si el usuario no provee la suya)
author_key = os.getenv("GROQ_API_KEY")
active_api_key = None

with st.sidebar:
    st.header(" Configuración ")
    
    # Campo para que el usuario ponga su propia llave
    user_key = st.text_input("Ingresa tu propia Groq API Key (opcional):", type="password")
    
    # Lógica de asignación de llave activa
    if user_key:
        active_api_key = user_key
        st.success("Usando API Key: demo ")
    elif author_key:
        if st.session_state.message_count < MAX_FREE_MESSAGES:
            active_api_key = author_key
            restantes = MAX_FREE_MESSAGES - st.session_state.message_count
            st.info(f"Usando cuota de la demo. Consultas restantes: {restantes}")
        else:
            st.warning("⚠️ Cuota de la demo agotada.")
            st.info("Para continuar, ingresa tu propia API Key de Groq.")
            st.link_button("Obtener API Key gratis", "https://console.groq.com/keys")
    
    st.divider()

# --- FLUJO PRINCIPAL DE LA APLICACIÓN ---

if not active_api_key:
    st.warning("Por favor, configura una API Key en el panel lateral para comenzar.")
else:
    # Registramos la llave en el entorno para LangChain
    os.environ["GROQ_API_KEY"] = active_api_key
    
    try:
        # Inicializamos el modelo (puedes cambiar a 'llama-3-8b-8192' si quieres ahorrar tokens)
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
       
        with st.sidebar:
            uploaded_files = st.file_uploader("Subí tus apuntes (PDF)", type="pdf", accept_multiple_files=True)

        if not uploaded_files:
            st.info("👋 ¡Hola! Subí tus PDFs en la barra lateral para empezar a estudiar.")
        else:
            # Procesamiento de documentos
            all_docs = []
            with st.status("Procesando documentos...", expanded=False) as status:
                for file in uploaded_files:
                    temp_path = f"temp_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    loader = PyPDFLoader(temp_path)
                    all_docs.extend(loader.load())
                    os.remove(temp_path)
                
                status.update(label="Creando base de conocimientos...", state="running")
                
                # Motor RAG con FAISS y Embeddings locales
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                chunks = text_splitter.split_documents(all_docs)
                
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                vectorstore = FAISS.from_documents(chunks, embeddings)
                status.update(label="¡Base de conocimientos lista!", state="complete", expanded=False)

            # Logica del chat e historial
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar historial de mensajes
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Entrada de nuevas preguntas
            if prompt_text := st.chat_input("Hacé una pregunta sobre tus archivos..."):
                
                # Verificamos si aún tiene cuota antes de procesar
                if not user_key and st.session_state.message_count >= MAX_FREE_MESSAGES:
                    st.error("Límite de demo alcanzado. Por favor, ingresa tu API Key en la barra lateral.")
                else:
                    # Añadir pregunta del usuario al chat
                    st.session_state.messages.append({"role": "user", "content": prompt_text})
                    with st.chat_message("user"):
                        st.markdown(prompt_text)

                    # Si usa la llave demo, aumentamos el contador
                    if not user_key:
                        st.session_state.message_count += 1

                    # Respuesta del RAG
                    template = """Usa el siguiente contexto para responder la pregunta de forma detallada.
                    Si no sabes la respuesta, simplemente di que no está en el texto, no inventes.
                    
                    Contexto:
                    {context}
                    
                    Pregunta: {question}"""
                    
                    prompt = ChatPromptTemplate.from_template(template)
                    
                    chain = (
                        {"context": vectorstore.as_retriever(search_kwargs={"k": 3}) | (lambda docs: "\n\n".join(d.page_content for d in docs)), 
                         "question": RunnablePassthrough()}
                        | prompt | llm | StrOutputParser()
                    )

                    with st.chat_message("assistant"):
                        with st.spinner("Analizando documentos..."):
                            response = chain.invoke(prompt_text)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Si fue consulta de cortesía, avisamos al final cuánto queda
                            if not user_key:
                                st.caption(f"Consultas de cortesía restantes: {MAX_FREE_MESSAGES - st.session_state.message_count}")

    except Exception as e:
        st.error(f"Se produjo un error: {e}")
