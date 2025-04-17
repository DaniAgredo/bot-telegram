import os
import logging
import asyncio
from flask import Flask, request
from dotenv import load_dotenv
import paypalrestsdk
import telegram
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Cargar las variables de entorno
load_dotenv()

# Configurar PayPal
paypalrestsdk.configure({
    'mode': 'live',
    'client_id': os.getenv('PAYPAL_CLIENT_ID'),
    'client_secret': os.getenv('PAYPAL_CLIENT_SECRET'),
})

# Flask App
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot corriendo correctamente"

@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('Paypal-Transmission-Sig')
    webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')

    if not webhook_id:
        return "Webhook ID no definido", 500

    verified = paypalrestsdk.notifications.WebhookEvent.verify(
        transmission_sig=signature,
        transmission_id=request.headers.get("Paypal-Transmission-Id"),
        transmission_time=request.headers.get("Paypal-Transmission-Time"),
        cert_url=request.headers.get("Paypal-Cert-Url"),
        auth_algo=request.headers.get("Paypal-Auth-Algo"),
        webhook_id=webhook_id,
        event_body=payload,
    )

    if verified:
        event = paypalrestsdk.notifications.WebhookEvent.from_json(payload)
        print(f"✅ Evento verificado: {event.event_type}")
    else:
        print("❌ Evento PayPal no verificado")

    return "", 200

@app.route('/webhook/telegram', methods=['POST'])
async def telegram_webhook():
    await bot_app.update_queue.put(Update.de_json(request.json, bot_app.bot))
    return '', 200

# Funciones del bot de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot activo desde Railway.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Este es el comando /help, ¿cómo puedo ayudarte?")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if 'hola' in text:
        await update.message.reply_text("¡Hola! ¿Qué necesitas?")
    else:
        await update.message.reply_text("No entendí eso, pero estoy aquí para ayudarte.")

# Configuración del bot
async def init_bot():
    global bot_app

    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # <- Asegúrate de tener esta variable en Railway

    if not TELEGRAM_TOKEN or not WEBHOOK_URL:
        raise ValueError("TELEGRAM_TOKEN o WEBHOOK_URL no están configurados.")

    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(CommandHandler('help', help_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    # Configurar webhook
    webhook_full_url = f"{WEBHOOK_URL}/webhook/telegram"
    await bot_app.bot.set_webhook(url=webhook_full_url)

    print(f"📡 Webhook de Telegram configurado en: {webhook_full_url}")

    return bot_app

# Ejecutar todo
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    bot_app = loop.run_until_complete(init_bot())

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
