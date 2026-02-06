FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definimos variables de entorno para Streamlit(debemos usar el puerto 7860 en HF Spaces)
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
# Cross-Origin Resource Sharing y protección XSRF deshabilitadas para HF Spaces
ENV STREAMLIT_SERVER_ENABLE_CORS=false 
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces usa el 7860
EXPOSE 7860

# El HEALTHCHECK también debe apuntar al 7860
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Forzamos los parámetros en el comando final
CMD ["streamlit", "run", "src/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]