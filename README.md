---
title: Estudio RAG Facu
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📚 Multi-PDF Private RAG Study Assistant

### 🎯 Objetivo
Este proyecto permite a estudiantes cargar múltiples archivos PDF de estudio y realizar consultas semánticas utilizando Inteligencia Artificial. A diferencia de un chat convencional, este sistema utiliza **RAG (Retrieval-Augmented Generation)** para responder basándose exclusivamente en los documentos proporcionados, evitando alucinaciones y manteniendo la privacidad de los datos.

### 🛠️ Tecnologías y ¿Por qué?
* **Llama 3.3 (via Groq):** Elegido como el "cerebro" (LLM) por su increíble velocidad de inferencia y capacidad de razonamiento gratuita.
* **LangChain (LCEL):** Utilizado para orquestar la lógica del RAG mediante cadenas modulares, permitiendo una fácil escalabilidad.
* **FAISS (Facebook AI Similarity Search):** Se seleccionó como base de datos vectorial por ser extremadamente ligera y evitar dependencias complejas de compilación (como C++) en sistemas Windows.
* **HuggingFace Embeddings (`all-MiniLM-L6-v2`):** Modelo de embeddings que corre localmente para transformar texto en vectores sin costo de API.
* **Streamlit:** Interfaz de usuario rápida y eficiente para una experiencia de chat intuitiva.

## 🔄 Arquitectura de Despliegue (CI/CD)

El proyecto utiliza un flujo de trabajo automatizado para garantizar que la versión en producción siempre esté sincronizada:

1. **Desarrollo Local:** Cambios en la lógica del RAG o la interfaz en VS Code.
2. **Control de Versiones:** `git push origin main` hacia GitHub.
3. **GitHub Actions:** Un runner de Ubuntu se activa automáticamente, autentica con Hugging Face mediante un `HF_TOKEN` y realiza un `git push --force` al Space.
4. **Hugging Face Spaces:** Detecta el cambio en el `Dockerfile`, recompila la imagen y despliega la nueva versión en minutos.

### 🚀 Cómo Correr Localmente

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/pattoor/RAG-Privado-Estudio.git
   cd RAG-Privado-Estudio
2. **Crear entorno virtual(opcional):**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Linux/Mac:
    source venv/bin/activate
3. **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
4. **Configurar API Key:**
    Crea un archivo .env o ingresa tu clave directamente en la interfaz de la App.
5. **Correr WebApp:**
    ```bash
    streamlit run app.py

#### Tips de Uso
Chunking: El sistema divide los textos en pedazos de 1000 caracteres. Si tus apuntes tienen tablas complejas, probá reduciendo este tamaño.

Contexto: Si la IA no responde algo, verificá que el PDF sea legible (que no sea una imagen escaneada sin OCR).

## 🌐 Live Demo
Podés probar la aplicación en vivo aquí: [https://huggingface.co/spaces/patoor/estudio-rag-facu]

---
AUTHOR: Patricio Romero | System Engineering Student 
