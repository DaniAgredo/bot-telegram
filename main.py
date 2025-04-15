import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configurar logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hola {user.mention_html()}, bienvenido al bot. ¿En qué puedo ayudarte?"
    )

# /help
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Este es un bot interactivo. Usa las opciones disponibles.")

# saludo
async def greet(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! ¿Cómo estás? Estoy aquí para ayudarte.")

# contactar con el creador
async def contact_me(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "¡Hola! Para hablar conmigo directamente, por favor, visita mi perfil de Telegram: @AgredoD"
    )

# métodos de pago
async def payment(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Aquí tienes los métodos de pago disponibles:\n"
        "1. PayPal: [Enlace de PayPal]\n"
        "2. Skrill: [Enlace de Skrill]\n"
        "3. Mercado Pago: [Enlace de Mercado Pago]"
    )

# manejar texto libre
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    if "hola" in user_message or "hello" in user_message:
        await greet(update, context)
    else:
        await update.message.reply_text("Lo siento, no entiendo ese comando. ¿Cómo puedo ayudarte?")

# función principal
def main() -> None:
    application = Application.builder().token("TU_TOKEN_AQUI").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)^hola$"), greet))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)^hello$"), greet))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)^hablar conmigo$"), contact_me))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)^opciones de pago$"), payment))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.Regex("(?i)^(hola|hello|hablar conmigo|opciones de pago)$"), handle_message)
    )

    application.run_polling()

if __name__ == "__main__":
    main()
