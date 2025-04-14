import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, ConversationHandler
)
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
    if choice == "1":
        await update.message.reply_text("✨ Estoy aquí para ti. ¿Qué quieres saber o decirme?")
        return SELECTING_OPTION
    elif choice == "2":
        await update.message.reply_text(
            "💳 Elige tu método de pago:\n"
            "1. PayPal\n"
            "2. Skrill (Próximamente)\n"
            "3. Mercado Pago"
        )
        return SELECTING_PAYMENT_METHOD
    else:
        await update.message.reply_text("Por favor escribe 1 o 2.")
        return SELECTING_OPTION

# Manejo del método de pago
async def payment_method_selected(update: Update, context: CallbackContext) -> int:
    method = update.message.text.strip()
    if method == "1":
        keyboard = [[InlineKeyboardButton("💸 Pagar con PayPal", url="https://paypal.me/dannielcampo?country.x=CO&locale.x=es_XC")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Haz clic en el botón para completar el pago:",
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

    elif method == "2":
        await update.message.reply_text("⚠️ Skrill aún no está activo, pero pronto estará disponible.")
        return ConversationHandler.END

    elif method == "3":
        keyboard = [[InlineKeyboardButton("💸 Pagar con Mercado Pago", url="TU_LINK_DE_MERCADOPAGO")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Haz clic en el botón para completar el pago:",
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

    else:
        await update.message.reply_text("Opción no válida. Escribe 1, 2 o 3.")
        return SELECTING_PAYMENT_METHOD

# Cancelar
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("❌ Conversación cancelada. ¡Nos vemos pronto!")
    return ConversationHandler.END

# Función principal
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", welcome_message),
                      MessageHandler(filters.TEXT & ~filters.COMMAND, welcome_message)],
        states={
            SELECTING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, option_selected)],
            SELECTING_PAYMENT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_method_selected)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
