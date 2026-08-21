#!/usr/bin/env python3
"""
Configuración centralizada del bot
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Token del bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configuración de logs
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Límites
MAX_VIDEO_SIZE_MB = int(os.getenv('MAX_VIDEO_SIZE_MB', 2000))
MAX_PROCESSING_TIME_SECONDS = int(os.getenv('MAX_PROCESSING_TIME_SECONDS', 1800))

# Directorios
TEMP_DIR = os.getenv('TEMP_DIR', './temp')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')

# Crear directorios si no existen
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Validar configuración
if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN no está configurado.\n"
        "1. Copia .env.example a .env\n"
        "2. Agrega tu token de Telegram\n"
        "3. Obtén tu token en: https://t.me/BotFather"
    )

print("✅ Configuración cargada correctamente")
