#!/usr/bin/env python3
"""
Bot de Telegram para comprimir videos - Versión Render
"""

import os
import logging
import asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError

# Importar el compresor de videos
try:
    from video_compressor import VideoCompressor
    FFMPEG_AVAILABLE = True
except Exception as e:
    FFMPEG_AVAILABLE = False
    print(f"⚠️ Advertencia: {e}")

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN no está configurado en las variables de entorno")
    raise ValueError(
        "BOT_TOKEN no está configurado.\n"
        "Agrega la variable de entorno BOT_TOKEN en Render Dashboard."
    )

logger.info("✅ Token de Telegram detectado")

# Crear directorios temporales
TEMP_DIR = Path("/tmp/downloads")
OUTPUT_DIR = Path("/tmp/compressed")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar compresor si FFmpeg está disponible
compressor = None
if FFMPEG_AVAILABLE:
    try:
        compressor = VideoCompressor()
        logger.info("✅ FFmpeg detectado - Compresión habilitada")
    except Exception as e:
        logger.warning(f"⚠️ FFmpeg no disponible: {e}")
        compressor = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida"""
    welcome_message = """
🎥 **¡Bienvenido al Bot de Compresión de Videos!**

Este bot comprime videos automáticamente y te envía el resultado.

**Cómo usar:**
1️⃣ Envía un video
2️⃣ Espera a que se comprima
3️⃣ Recibe el video comprimido

**Opciones disponibles:**
✅ Envía un video para comprimirlo
✅ Usa /help para más información
✅ Usa /settings para configurar la compresión

¿Qué deseas hacer?
    """
    
    keyboard = [
        [InlineKeyboardButton("Comprimir Video", callback_data='compress')],
        [InlineKeyboardButton("Ayuda", callback_data='help')],
        [InlineKeyboardButton("Configuración", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Mostrar ayuda"""
    help_text = """
📖 **GUÍA DE USO**

**Paso 1:** Envía un video
**Paso 2:** Selecciona la calidad (opcional con /settings)
**Paso 3:** Espera a que se comprima
**Paso 4:** Recibe tu video comprimido

**Formatos soportados:**
• MP4, AVI, MOV, MKV, FLV, WebM, 3GP

**Niveles de Calidad:**
🎯 **Baja:** 50-70% más pequeño
⚖️ **Media:** 40-60% más pequeño (recomendado)
🎬 **Alta:** 20-40% más pequeño

**Información:**
• Tiempo de compresión: Depende del tamaño
• Máximo: 2GB por video
• El bot mantiene la relación de aspecto

¿Preguntas? Usa /settings
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /settings - Configuración"""
    settings_text = "⚙️ **CONFIGURACIÓN DE COMPRESIÓN**\n\n"
    settings_text += "Selecciona la calidad de compresión:\n"
    
    keyboard = [
        [InlineKeyboardButton("🎯 Baja (50-70% reducción)", callback_data='quality_low')],
        [InlineKeyboardButton("⚖️ Media (40-60% reducción)", callback_data='quality_medium')],
        [InlineKeyboardButton("🎬 Alta (20-40% reducción)", callback_data='quality_high')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de botones inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'compress':
        await query.edit_message_text(
            text="📹 Envía el video que deseas comprimir...",
            parse_mode='Markdown'
        )
    elif query.data == 'help':
        help_text = """
📖 **GUÍA DE USO**

1. Envía un video
2. Espera a que se comprima
3. Recibe el resultado

**Formatos soportados:**
• MP4, AVI, MOV, MKV, FLV, WebM

**Tiempo de espera:**
Depende del tamaño del video
        """
        await query.edit_message_text(text=help_text, parse_mode='Markdown')
    elif query.data == 'settings':
        settings_text = "⚙️ **CONFIGURACIÓN**\n\nSelecciona la calidad:\n"
        keyboard = [
            [InlineKeyboardButton("🎯 Baja", callback_data='quality_low')],
            [InlineKeyboardButton("⚖️ Media", callback_data='quality_medium')],
            [InlineKeyboardButton("🎬 Alta", callback_data='quality_high')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=settings_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif query.data.startswith('quality_'):
        quality = query.data.split('_')[1]
        context.user_data['quality'] = quality
        quality_names = {'low': '🎯 Baja', 'medium': '⚖️ Media', 'high': '🎬 Alta'}
        await query.edit_message_text(
            text=f"✅ Calidad configurada: {quality_names.get(quality, quality)}\n\nAhora envía un video para comprimir."
        )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de videos enviados"""
    try:
        video = update.message.video
        
        if not video:
            await update.message.reply_text("❌ Por favor, envía un archivo de video válido.")
            return
        
        # Verificar tamaño
        file_size_mb = video.file_size / (1024 * 1024)
        if file_size_mb > 2000:
            await update.message.reply_text(
                f"❌ El video es muy grande ({file_size_mb:.2f} MB)\n"
                f"Máximo permitido: 2000 MB"
            )
            return
        
        # Obtener configuración del usuario
        quality = context.user_data.get('quality', 'medium')
        
        # Mensaje inicial
        progress_msg = await update.message.reply_text(
            f"⏳ Procesando video...\n\n"
            f"📊 Información:\n"
            f"  • Tamaño: {file_size_mb:.2f} MB\n"
            f"  • Calidad: {quality.capitalize()}\n\n"
            f"Descargando... 0%"
        )
        
        try:
            # Descargar video
            logger.info(f"Descargando video desde Telegram...")
            file = await context.bot.get_file(video.file_id)
            
            # Generar nombre único
            video_filename = f"{video.file_id}_{video.file_unique_id}.mp4"
            video_path = TEMP_DIR / video_filename
            
            # Descargar
            await file.download_to_drive(str(video_path))
            logger.info(f"✅ Video descargado: {video_path}")
            
            # Actualizar progreso
            await progress_msg.edit_text(
                f"⏳ Procesando video...\n\n"
                f"Descargando... 100%\n"
                f"Comprimiendo... 0%"
            )
            
            # Comprimir si FFmpeg está disponible
            if not compressor:
                await progress_msg.edit_text(
                    "❌ FFmpeg no está disponible en este servidor.\n\n"
                    "El bot está en modo demo. Para compresión real, usa una versión local."
                )
                return
            
            output_filename = f"{video.file_id}_compressed.mp4"
            output_path = OUTPUT_DIR / output_filename
            
            # Ejecutar compresión
            logger.info(f"Iniciando compresión con calidad: {quality}")
            success = compressor.compress(str(video_path), str(output_path), quality)
            
            if not success:
                await progress_msg.edit_text(
                    "❌ Error al comprimir el video.\n\n"
                    "Por favor, intenta con otro video."
                )
                return
            
            # Actualizar progreso
            await progress_msg.edit_text(
                f"⏳ Procesando video...\n\n"
                f"Descargando... 100%\n"
                f"Comprimiendo... 100%\n"
                f"Enviando... 0%"
            )
            
            # Obtener información de archivos
            original_size = video_path.stat().st_size / (1024 * 1024)
            compressed_size = output_path.stat().st_size / (1024 * 1024)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            logger.info(f"Compresión exitosa: {original_size:.2f}MB → {compressed_size:.2f}MB ({reduction:.1f}%)")
            
            # Enviar video comprimido
            with open(output_path, 'rb') as video_file:
                await update.message.reply_video(
                    video_file,
                    caption=f"✅ **¡Video comprimido exitosamente!**\n\n"
                            f"📊 **Estadísticas:**\n"
                            f"  • Tamaño original: {original_size:.2f} MB\n"
                            f"  • Tamaño comprimido: {compressed_size:.2f} MB\n"
                            f"  • Reducción: {reduction:.1f}%\n"
                            f"  • Calidad: {quality.capitalize()}",
                    parse_mode='Markdown'
                )
            
            # Eliminar archivo de progreso
            await progress_msg.delete()
            
            # Limpiar archivos temporales
            logger.info("Limpiando archivos temporales...")
            video_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
            
        except TelegramError as e:
            logger.error(f"Error de Telegram: {e}")
            await progress_msg.edit_text(
                f"❌ Error de comunicación con Telegram:\n\n"
                f"`{str(e)}`",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error procesando video: {e}", exc_info=True)
            await progress_msg.edit_text(
                f"❌ Error al procesar el video:\n\n"
                f"`{str(e)}`",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error en handle_video: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de errores"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


def main() -> None:
    """Iniciar el bot"""
    try:
        logger.info("=" * 50)
        logger.info("🚀 INICIANDO BOT DE COMPRESIÓN DE VIDEOS")
        logger.info("=" * 50)
        logger.info(f"Token detectado: {BOT_TOKEN[:10]}...")
        logger.info(f"FFmpeg disponible: {'✅ Sí' if FFMPEG_AVAILABLE else '❌ No'}")
        logger.info(f"Directorio temporal: {TEMP_DIR}")
        logger.info(f"Directorio de salida: {OUTPUT_DIR}")
        logger.info("=" * 50)
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Comandos
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("settings", settings_command))
        
        # Botones
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Videos
        application.add_handler(MessageHandler(filters.VIDEO, handle_video))
        
        # Errores
        application.add_error_handler(error_handler)
        
        # Iniciar bot
        logger.info("✅ Bot iniciado exitosamente. Escuchando mensajes...")
        logger.info("=" * 50)
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Error fatal al iniciar el bot: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
