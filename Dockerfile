FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos primero
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del bot
COPY main.py .
COPY video_compressor.py .
COPY config.py .

# Crear directorios necesarios
RUN mkdir -p temp output downloads compressed

# Comando para ejecutar el bot
CMD ["python", "main.py"]
