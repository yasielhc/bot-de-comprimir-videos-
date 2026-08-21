#!/usr/bin/env python3
"""
Bot de Telegram para comprimir videos
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

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

logger.info("✅ Bot inicializando...")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida"""
    welcome_message = """
🎥 **¡Bienvenido al Bot de Compresión de Videos!**

Este bot te ayuda a comprimir videos de manera rápida y fácil.

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

1. **Enviar video:** Solo envía un video al chat
2. **Esperar:** El bot procesará el video
3. **Descargar:** Recibirás el video comprimido

**Formatos soportados:**
• MP4, AVI, MOV, MKV, FLV, WebM

**Configuración de compresión:**
• Calidad: Baja, Media, Alta
• Resolución: 480p, 720p, 1080p

**Límites:**
• Tamaño máximo: 2GB
• Tiempo máximo de espera: 30 minutos

¿Preguntas? Usa /settings
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /settings - Configuración"""
    settings_text = "⚙️ **CONFIGURACIÓN DE COMPRESIÓN**\n\n"
    settings_text += "Selecciona la calidad de compresión:\n"
    
    keyboard = [
        [InlineKeyboardButton("🎯 Baja (más pequeño)", callback_data='quality_low')],
        [InlineKeyboardButton("⚖️ Media (equilibrado)", callback_data='quality_medium')],
        [InlineKeyboardButton("🎬 Alta (mejor calidad)", callback_data='quality_high')]
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

1. **Enviar video:** Solo envía un video al chat
2. **Esperar:** El bot procesará el video
3. **Descargar:** Recibirás el video comprimido

**Formatos soportados:**
• MP4, AVI, MOV, MKV, FLV, WebM

**Límites:**
• Tamaño máximo: 2GB
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
        # Por ahora, solo confirmamos que recibimos el video
        video = update.message.video
        
        if not video:
            await update.message.reply_text("❌ Por favor, envía un archivo de video válido.")
            return
        
        file_size_mb = video.file_size / (1024 * 1024)
        
        # Mensaje de confirmación (sin procesar aún)
        await update.message.reply_text(
            f"📹 Video recibido\n"
            f"Tamaño: {file_size_mb:.2f} MB\n\n"
            f"ℹ️ La compresión de videos requiere FFmpeg.\n"
            f"🔧 Para usar la compresión completa, ejecuta este bot localmente.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error en handle_video: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de errores"""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Iniciar el bot"""
    try:
        logger.info("🚀 Iniciando Bot de Compresión de Videos...")
        logger.info(f"Token detectado: {BOT_TOKEN[:10]}...")
        
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
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar el bot: {e}")
        raise


if __name__ == '__main__':
    main()
