#!/usr/bin/env python3
"""
Bot de Telegram para comprimir videos - versión robusta.
"""

import logging
import os
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

try:
    from video_compressor import VideoCompressor
except Exception as exc:  # pragma: no cover
    VideoCompressor = None
    print(f"⚠️ Advertencia: {exc}")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN no está configurado en las variables de entorno")
    raise ValueError(
        "BOT_TOKEN no está configurado.\n"
        "Agrega la variable de entorno BOT_TOKEN en Render Dashboard."
    )

TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/downloads"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/compressed"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_VIDEO_SIZE_MB = float(os.getenv("MAX_VIDEO_SIZE_MB", 45))
MAX_ALLOWED_SIZE_BYTES = int(MAX_VIDEO_SIZE_MB * 1024 * 1024)

compressor = None
if VideoCompressor is not None:
    try:
        compressor = VideoCompressor()
        logger.info("✅ FFmpeg detectado - Compresión habilitada")
    except Exception as exc:
        logger.warning(f"⚠️ FFmpeg no disponible: {exc}")
        compressor = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Mensaje de bienvenida."""
    text = """
🎥 **¡Bienvenido al Bot de Compresión de Videos!**

Envía un video y lo comprimiré para que pueda enviarse por Telegram.

**Cómo usar:**
1️⃣ Envía un video
2️⃣ Espera la compresión
3️⃣ Recibe el video comprimido

**Calidad disponible:**
🎯 Baja
⚖️ Media
🎬 Alta

Usa /settings para elegir la calidad.
    """
    keyboard = [
        [InlineKeyboardButton("Comprimir Video", callback_data="compress")],
        [InlineKeyboardButton("Ayuda", callback_data="help")],
        [InlineKeyboardButton("Configuración", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Mostrar ayuda."""
    help_text = """
📖 **GUÍA DE USO**

1. Envía un video
2. Selecciona la calidad si quieres ajustar la compresión
3. Espera a que termine el proceso
4. Recibe el archivo comprimido

**Límites prácticos:**
• Telegram no admite archivos muy grandes en el envío final
• El bot comprime cada video para intentar dejarlo dentro del límite

**Calidades:**
🎯 Baja = mejor compresión
⚖️ Media = equilibrio
🎬 Alta = mejor calidad
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /settings - Configuración."""
    settings_text = "⚙️ **CONFIGURACIÓN DE COMPRESIÓN**\n\nSelecciona la calidad de compresión:\n"
    keyboard = [
        [InlineKeyboardButton("🎯 Baja", callback_data="quality_low")],
        [InlineKeyboardButton("⚖️ Media", callback_data="quality_medium")],
        [InlineKeyboardButton("🎬 Alta", callback_data="quality_high")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de botones inline."""
    query = update.callback_query
    await query.answer()

    if query.data == "compress":
        await query.edit_message_text("📹 Envía el video que deseas comprimir...", parse_mode="Markdown")
    elif query.data == "help":
        await query.edit_message_text(
            "📖 **GUÍA DE USO**\n\n1. Envía un video\n2. Espera la compresión\n3. Recibe el video resultante",
            parse_mode="Markdown",
        )
    elif query.data == "settings":
        settings_text = "⚙️ **CONFIGURACIÓN**\n\nSelecciona la calidad:\n"
        keyboard = [
            [InlineKeyboardButton("🎯 Baja", callback_data="quality_low")],
            [InlineKeyboardButton("⚖️ Media", callback_data="quality_medium")],
            [InlineKeyboardButton("🎬 Alta", callback_data="quality_high")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=settings_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif query.data.startswith("quality_"):
        quality = query.data.split("_")[1]
        context.user_data["quality"] = quality
        quality_names = {"low": "🎯 Baja", "medium": "⚖️ Media", "high": "🎬 Alta"}
        await query.edit_message_text(
            text=f"✅ Calidad configurada: {quality_names.get(quality, quality)}\n\nAhora envía un video para comprimir."
        )


async def _resolve_video_file(message) -> tuple[str | None, str | None, int | None, str | None]:
    """Devuelve (file_id, file_name, file_size, mime_type) para videos o documentos/video."""
    if message.video:
        video = message.video
        return (
            video.file_id,
            video.file_name or f"{video.file_unique_id}.mp4",
            video.file_size or 0,
            "video/mp4",
        )

    if message.document and message.document.mime_type and "video" in message.document.mime_type.lower():
        doc = message.document
        return (
            doc.file_id,
            doc.file_name or f"{doc.file_unique_id}.mp4",
            doc.file_size or 0,
            doc.mime_type,
        )

    return (None, None, None, None)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de videos enviados por Telegram."""
    try:
        message = update.message
        if message is None:
            return

        video_file_id, file_name, file_size, mime_type = await _resolve_video_file(message)
        if not video_file_id:
            await message.reply_text("❌ Por favor, envía un archivo de video válido.")
            return

        file_size_mb = (file_size or 0) / (1024 * 1024)
        if file_size and file_size > MAX_ALLOWED_SIZE_BYTES:
            await message.reply_text(
                f"❌ El video es demasiado grande para Telegram ({file_size_mb:.2f} MB).\n"
                f"Máximo recomendado: {MAX_VIDEO_SIZE_MB:.0f} MB para un procesamiento seguro.\n"
                f"Prueba con un video más corto o de menor resolución."
            )
            return

        quality = context.user_data.get("quality", "medium")
        progress_msg = await message.reply_text(
            f"⏳ Procesando video...\n\n"
            f"📊 Información:\n"
            f"  • Tamaño: {file_size_mb:.2f} MB\n"
            f"  • Calidad: {quality.capitalize()}\n\n"
            f"Descargando... 0%"
        )

        try:
            logger.info("Descargando video desde Telegram...")
            tg_file = await context.bot.get_file(video_file_id)
            safe_name = (file_name or f"{video_file_id}.mp4").replace("/", "_")
            local_path = TEMP_DIR / f"{video_file_id}_{safe_name}"
            await tg_file.download_to_drive(str(local_path))
            logger.info(f"✅ Video descargado: {local_path}")

            await progress_msg.edit_text(
                f"⏳ Procesando video...\n\n"
                f"Descargando... 100%\n"
                f"Comprimiendo... 0%"
            )

            if compressor is None:
                await progress_msg.edit_text(
                    "❌ FFmpeg no está disponible en este servidor.\n\n"
                    "El bot no puede comprimir videos sin FFmpeg."
                )
                return

            output_name = f"{video_file_id}_compressed.mp4"
            output_path = OUTPUT_DIR / output_name
            success = compressor.compress(str(local_path), str(output_path), quality)

            if not success:
                await progress_msg.edit_text(
                    "❌ Error al comprimir el video.\n\n"
                    "Intenta con otro archivo o una versión más pequeña."
                )
                return

            original_size = local_path.stat().st_size / (1024 * 1024)
            compressed_size = output_path.stat().st_size / (1024 * 1024)
            reduction = ((original_size - compressed_size) / original_size) * 100 if original_size else 0.0

            await progress_msg.edit_text(
                f"⏳ Procesando video...\n\n"
                f"Descargando... 100%\n"
                f"Comprimiendo... 100%\n"
                f"Enviando... 0%"
            )

            if compressed_size > MAX_VIDEO_SIZE_MB:
                logger.warning(f"Archivo comprimido aún grande: {compressed_size:.2f} MB")
                await progress_msg.edit_text(
                    "⚠️ El video comprimido sigue siendo demasiado grande para enviarlo por Telegram.\n\n"
                    "Prueba con un video más corto o reduce aún más la resolución."
                )
                return

            with open(output_path, "rb") as video_file:
                await message.reply_video(
                    video_file,
                    caption=(
                        "✅ **¡Video comprimido exitosamente!**\n\n"
                        "📊 **Estadísticas:**\n"
                        f"  • Tamaño original: {original_size:.2f} MB\n"
                        f"  • Tamaño comprimido: {compressed_size:.2f} MB\n"
                        f"  • Reducción: {reduction:.1f}%\n"
                        f"  • Calidad: {quality.capitalize()}"
                    ),
                    supports_streaming=True,
                    parse_mode="Markdown",
                )

            await progress_msg.delete()
            logger.info("Limpiando archivos temporales...")
            local_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

        except TelegramError as exc:
            logger.error(f"Error de Telegram: {exc}")
            await progress_msg.edit_text(
                f"❌ Error de comunicación con Telegram:\n\n`{exc}`",
                parse_mode="Markdown",
            )
        except Exception as exc:
            logger.error(f"Error procesando video: {exc}", exc_info=True)
            await progress_msg.edit_text(
                f"❌ Error al procesar el video:\n\n`{exc}`",
                parse_mode="Markdown",
            )

    except Exception as exc:
        logger.error(f"Error en handle_video: {exc}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {exc}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo de errores del bot."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


def main() -> None:
    """Iniciar el bot."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO BOT DE COMPRESIÓN DE VIDEOS")
        logger.info("=" * 60)
        logger.info(f"Token detectado: {BOT_TOKEN[:10]}...")
        logger.info(f"FFmpeg disponible: {'✅ Sí' if compressor is not None else '❌ No'}")
        logger.info(f"Directorio temporal: {TEMP_DIR}")
        logger.info(f"Directorio de salida: {OUTPUT_DIR}")
        logger.info(f"Límite operativo: {MAX_VIDEO_SIZE_MB} MB")
        logger.info("=" * 60)

        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
        application.add_error_handler(error_handler)

        logger.info("✅ Bot iniciado exitosamente. Escuchando mensajes...")
        logger.info("=" * 60)
        application.run_polling(drop_pending_updates=True)
    except Exception as exc:
        logger.error(f"❌ Error fatal al iniciar el bot: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
