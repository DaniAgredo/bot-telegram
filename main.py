import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Habilitar el registro para ver los errores y el funcionamiento del bot
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
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
        "3. Mercado Libre: [Enlace de Mercado Libre]"
    )

# Comando para manejar texto general
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    
    # Si el mensaje es "hola" o "hello", se activará la respuesta de saludo
    if "hola" in user_message or "hello" in user_message:
        await greet(update, context)
    else:
        await update.message.reply_text("Lo siento, no entiendo ese comando. ¿Cómo puedo ayudarte?")
        
# Función para iniciar el bot
def main() -> None:
    # Crear la aplicación de Telegram
    application = Application.builder().token("TU_TOKEN_AQUI").build()

    # Comandos del bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Responder a los mensajes que contengan "hola" o "hello"
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(hola|hello)$'), greet))

    # Responder a la opción de contactar directamente
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^hablar conmigo$'), contact_me))

    # Responder a la opción de pagos
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^opciones de pago$'), payment))

    # Manejar mensajes generales
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex('^(hola|hello|opciones de pago|hablar conmigo)$'), handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == "__main__":
    main()
