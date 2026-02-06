import streamlit as st
import os
from dotenv import load_dotenv # Importante para local

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 0. Cargar variables de entorno (Solo para local, en HF no hará nada)
load_dotenv()

# 1. Configuración de la interfaz
st.set_page_config(page_title="IA de Estudio", layout="wide", page_icon="📚")
st.title("📚 Asistente IA de Estudio: Multi-RAG")

# 2. Manejo de API Key
# Intenta obtenerla de: 1. El entorno (Secrets de HF o .env local)
api_key = os.getenv("GROQ_API_KEY")

# Si no existe en el entorno, la pide por el Sidebar
if not api_key:
    with st.sidebar:
        st.header("Configuración de Seguridad")
        api_key = st.text_input("Introduce tu Groq API Key:", type="password")
        if not api_key:
            st.info("💡 Tip: Para no escribirla cada vez, configurala en un archivo .env local o en los Secrets de HF.")
            st.link_button("Obtener API Key", "https://console.groq.com/keys")

if not api_key:
    st.warning("⚠️ Se requiere una API Key de Groq para funcionar.")
else:
    os.environ["GROQ_API_KEY"] = api_key
    
    # Inicializamos el modelo (usamos Try/Except por si la Key es inválida)
    try:
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
        
        # 3. Sidebar para subir archivos
        with st.sidebar:
            st.divider()
            uploaded_files = st.file_uploader("Subí tus apuntes (PDF)", type="pdf", accept_multiple_files=True)

        if not uploaded_files:
            st.info("👋 ¡Hola! Subí tus PDFs en la barra lateral para empezar a estudiar.")
        else:
            all_docs = []
            # Spinner para que el usuario sepa que está procesando
            with st.status("Procesando documentos...", expanded=False) as status:
                for file in uploaded_files:
                    # Guardar temporalmente en la raíz
                    temp_path = f"temp_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    loader = PyPDFLoader(temp_path)
                    all_docs.extend(loader.load())
                    os.remove(temp_path) # Limpiamos el temporal inmediatamente
                
                status.update(label="Creando base de conocimientos...", state="running")
                
                # 4. Motor RAG con FAISS
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
                chunks = text_splitter.split_documents(all_docs)
                
                # Descarga el modelo de embeddings (all-MiniLM-L6-v2 es muy ligero)
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                vectorstore = FAISS.from_documents(chunks, embeddings)
                status.update(label="¡Listo para preguntar!", state="complete", expanded=False)

            # 5. Lógica de Chat (Mantenemos tu historial de sesión)
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar historial
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Input del usuario
            if prompt_text := st.chat_input("Hacé una pregunta sobre tus archivos..."):
                st.session_state.messages.append({"role": "user", "content": prompt_text})
                with st.chat_message("user"):
                    st.markdown(prompt_text)

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
                    with st.spinner("Pensando..."):
                        response = chain.invoke(prompt_text)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
    
    except Exception as e:
        st.error(f"Hubo un error con la API Key o el modelo: {e}")
    