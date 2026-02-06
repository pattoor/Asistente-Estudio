FROM python:3.11-slim

WORKDIR /app

# Instalación de dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos primero para aprovechar la cache de Docker
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt # Agregamos --no-cache-dir para que la imagen de Docker sea más liviana y buildee más rápido.

# Copiamos todo el contenido del proyecto
COPY . .

# Exponemos el puerto que exige Hugging Face
EXPOSE 7860

# Corregimos el HEALTHCHECK para que apunte al puerto correcto (7860)
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Comando de ejecución
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
