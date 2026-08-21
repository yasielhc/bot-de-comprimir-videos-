FROM python:3.11-slim

# Instalar FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
COPY main.py .
COPY video_compressor.py .
COPY config.py .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios
RUN mkdir -p temp output downloads compressed

# Ejecutar el bot
CMD ["python", "main.py"]
