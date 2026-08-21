FROM python:3.11

# Instalar FFmpeg y otras dependencias necesarias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verificar que FFmpeg está instalado
RUN ffmpeg -version

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del bot
COPY main.py .
COPY video_compressor.py .
COPY config.py .

# Crear directorios necesarios
RUN mkdir -p /tmp/downloads /tmp/compressed /app/temp /app/output

# Dar permisos de escritura
RUN chmod -R 777 /tmp/downloads /tmp/compressed /app/temp /app/output

# Variable de entorno para Python
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el bot
CMD ["python", "main.py"]
