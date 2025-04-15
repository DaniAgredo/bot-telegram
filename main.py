import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hola {user.mention_html()}, bienvenido al bot. ¿En qué puedo ayudarte?"
    )

# Comando /help
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Este es un bot interactivo. Usa las opciones disponibles.")

# Respuesta a "hola" o "hello"
async def greet(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    if "hola" in user_message or "hello" in user_message:
        await update.message.reply_text("¡Hola! ¿Cómo estás? Estoy aquí para ayudarte.")

# Respuesta a la opción de contactar con el creador del bot
async def contact_me(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "¡Hola! Para hablar conmigo directamente, por favor, visita mi perfil de Telegram: @AgredoD"
    )

# Respuesta a las opciones de pago
async def payment(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Aquí tienes los métodos de pago disponibles:\n"
        "1. PayPal: [Enlace de PayPal]\n"
        "2. Skrill: [Enlace de Skrill]\n"
        "3. Mercado Pago: [Enlace de Mercado Pago]"
    )

# Mensaje general
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    if "hola" in user_message or "hello" in user_message:
        await greet(update, context)
    else:
        await update.message.reply_text("Lo siento, no entiendo ese comando. ¿Cómo puedo ayudarte?")

# Función principal para ejecutar el bot
def main() -> None:
    import os
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    application = Application.builder().token(TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Respuestas específicas
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(hola|hello)$'), greet))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^hablar conmigo$', flags=re.IGNORECASE), contact_me))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^opciones de pago$', flags=re.IGNORECASE), payment))

    # Mensajes generales
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex('^(hola|hello|opciones de pago|hablar conmigo)$'), handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
