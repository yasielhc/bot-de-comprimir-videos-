# 🎥 Bot de Compresión de Videos en Telegram

Un bot inteligente para Telegram que comprime videos manteniendo buena calidad. Perfecto para reducir tamaño de archivos y ahorrar almacenamiento.

## ✨ Características

- ✅ **Compresión rápida** - Reduce el tamaño de videos significativamente
- ✅ **3 niveles de calidad** - Baja, Media, Alta
- ✅ **Interfaz amigable** - Botones inline para fácil uso
- ✅ **Múltiples formatos** - Soporta MP4, AVI, MOV, MKV, FLV, WebM
- ✅ **Estadísticas** - Muestra tamaño original, comprimido y porcentaje de reducción
- ✅ **Procesamiento asincrónico** - No bloquea otras conversaciones

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/yasielhc/bot-de-comprimir-videos-.git
cd bot-de-comprimir-videos-
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 5. Configurar el token

1. Abre [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot con `/newbot`
3. Copia el token
4. Crea un archivo `.env`:

```bash
cp .env.example .env
```

5. Edita `.env` y pega tu token:

```env
BOT_TOKEN=123456789:ABCdefGHIjklmNOpqrstUVwxyz
```

### 6. Ejecutar el bot

```bash
python main.py
```

## 🐳 Instalación con Docker

```bash
# Construir imagen
docker build -t telegram-video-compressor .

# Ejecutar contenedor
docker run -e BOT_TOKEN="tu_token_aqui" telegram-video-compressor
```

## ☁️ Desplegar en Render

1. Pushea tu código a GitHub
2. Ve a [Render.com](https://render.com)
3. Conecta tu repositorio de GitHub
4. Crea un nuevo servicio Web
5. Render detectará automáticamente `render.yaml`
6. Agrega tu `BOT_TOKEN` en las variables de entorno
7. ¡Listo! Tu bot estará en línea

## 📖 Uso

### Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida y opciones principales |
| `/help` | Muestra guía de uso y información |
| `/settings` | Configura el nivel de calidad |

### Pasos para comprimir un video

1. Inicia una conversación con el bot
2. Escribe `/start`
3. Selecciona "Comprimir Video" o envía un video directamente
4. (Opcional) Personaliza la calidad con `/settings`
5. Envía el video que deseas comprimir
6. ¡El bot procesará y te enviará el video comprimido!

## ⚙️ Niveles de Compresión

### 🎯 Baja (Máxima compresión)
- **Tamaño:** Muy pequeño (50-70% de reducción)
- **Calidad:** Notablemente reducida
- **Uso:** Cuando el tamaño es lo más importante
- **Resolución:** 640x480

### ⚖️ Media (Recomendado)
- **Tamaño:** Moderado (40-60% de reducción)
- **Calidad:** Buena relación tamaño/calidad
- **Uso:** La mayoría de casos
- **Resolución:** 1280x720

### 🎬 Alta (Mejor calidad)
- **Tamaño:** Mayor (20-40% de reducción)
- **Calidad:** Muy buena, casi imperceptible
- **Uso:** Cuando la calidad es importante
- **Resolución:** 1920x1080

## 🛠️ Estructura del Proyecto

```
bot-de-comprimir-videos-/
├── main.py                 # Bot principal
├── video_compressor.py     # Módulo de compresión
├── config.py              # Configuración centralizada
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Configuración Docker
├── render.yaml            # Configuración Render
├── .env.example           # Plantilla de configuración
├── .gitignore             # Archivos a ignorar
├── README.md              # Este archivo
└── LICENSE                # Licencia MIT
```

## 📊 Ejemplo de Salida

```
✅ ¡Video comprimido exitosamente!

📊 Estadísticas:
  • Tamaño original: 150.50 MB
  • Tamaño comprimido: 45.30 MB
  • Reducción: 69.9%
  • Calidad: Medium
```

## 🚨 Solución de Problemas

### "FFmpeg no está instalado"
```bash
ffmpeg -version
```

### "Error al procesar el video"
- Verifica que el archivo sea un video válido
- Comprueba que tienes suficiente espacio en disco
- Intenta con un video más pequeño primero

### "El bot no responde"
- Verifica que el `BOT_TOKEN` sea correcto
- Comprueba tu conexión a internet
- Mira los logs para más detalles

## 📝 Variables de Entorno

```env
BOT_TOKEN=tu_token_aqui        # Token de Telegram (requerido)
LOG_LEVEL=INFO                 # Nivel de logs
MAX_VIDEO_SIZE_MB=2000         # Tamaño máximo en MB
MAX_PROCESSING_TIME_SECONDS=1800 # Tiempo máximo en segundos
TEMP_DIR=./temp                # Directorio temporal
OUTPUT_DIR=./output            # Directorio de salida
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature')`
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

- **GitHub:** [@yasielhc](https://github.com/yasielhc)
- **Telegram:** [@YasielHernandez](https://t.me/YasielHernandez)

## ⭐ Dale una Estrella

Si te gusta este proyecto, ¡por favor dame una ⭐ en GitHub!

---

**Versión:** 1.0.0  
**Última actualización:** Agosto 2026
