import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Estados
SELECTING_OPTION, SELECTING_PAYMENT_METHOD = range(2)

# Bienvenida si escriben "hola"
async def welcome_message(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    if "hola" in text or "buenas" in text or "/start" in text:
        await update.message.reply_text(
            "👋 *¡Bienvenido al canal exclusivo!* Soy tu asistente personal.\n\n"
            "¿Qué deseas hacer?\n\n"
            "1️⃣ *Hablar conmigo directamente*\n"
            "2️⃣ *Unirte al canal VIP por solo $9.99* 🔥\n\n"
            "Escribe `1` o `2` para continuar.",
            parse_mode="Markdown"
        )
        return SELECTING_OPTION
    else:
        await update.message.reply_text("¿Cómo puedo ayudarte? Escribe 'hola' para ver las opciones.")
        return SELECTING_OPTION

# Elegir entre hablar o pagar
async def option_selected(update: Update, context: CallbackContext) -> int:
    choice = update.message.text.strip()

    # Si elige la opción 1 (hablar)
    if choice == "1":
        await update.message.reply_text("✨ Estoy aquí para ti. ¿Qué quieres saber o decirme?")
        return SELECTING_OPTION

    # Si elige la opción 2 (pagar)
    elif choice == "2":
        keyboard = [
            [InlineKeyboardButton("💸 Pagar con PayPal", url="https://paypal.me/dannielcampo?country.x=CO&locale.x=es_XC")],
            [InlineKeyboardButton("💸 Pagar con Skrill", url="https://skrill.me/rq/Daniel/9.99/USD?key=4kThKylj3LQbd3ROKmJnfvC2hVs")],
            [InlineKeyboardButton("💸 Pagar con Mercado Pago", url="https://mpago.li/2Qg3F6v")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "💳 Elige tu método de pago para acceder al canal VIP:",
            reply_markup=reply_markup
        )
        await update.message.reply_text(
            "✅ Cuando termines tu pago, espera unos segundos.\n"
            "Te daremos acceso automáticamente si todo está bien registrado.\n"
            "Escribe 'hola' si quieres volver al menú."
        )
        await asyncio.sleep(10)
        await update.message.reply_text("¿Deseas hacer algo más? Escribe 'hola' para ver el menú nuevamente.")
        return ConversationHandler.END

    # Si no se elige 1 ni 2, pedimos que ingrese una opción válida
    else:
        await update.message.reply_text("Por favor escribe 1 o 2.")
        return SELECTING_OPTION

# Cancelar
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("❌ Conversación cancelada. ¡Nos vemos pronto!")
    return ConversationHandler.END

# Función principal
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", welcome_message),
            MessageHandler(filters.TEXT & ~filters.COMMAND, welcome_message)
        ],
        states={
            SELECTING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, option_selected)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
