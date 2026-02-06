FROM python:3.11-slim

WORKDIR /app
# Instalación de dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos primero para aprovechar la cache de Docker. --no-cache-dir es para que deploye mas rapido
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido del proyecto
COPY . .

# Exponemos el puerto que exige Hugging Face
EXPOSE 8501

# Corregimos el HEALTHCHECK para que apunte al puerto correcto (7860)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de ejecución
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
