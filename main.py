import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, request
from dotenv import load_dotenv
import paypalrestsdk

# Cargar variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')

# Inicializar PayPal SDK
paypalrestsdk.configure({
    'mode': 'live',
    'client_id': PAYPAL_CLIENT_ID,
    'client_secret': PAYPAL_CLIENT_SECRET
})

# Logging
logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)

@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('Paypal-Transmission-Sig')

    if not signature:
        return "No Signature", 400

    verify = paypalrestsdk.notifications.webhook_event.verify(
        signature, payload, PAYPAL_WEBHOOK_ID
    )

    if verify:
        event = paypalrestsdk.notifications.WebhookEvent.from_json(payload)
        print("✅ Evento válido recibido de PayPal:", event)
    else:
        print("❌ Evento inválido.")
    return '', 200

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('¡Hola! Soy tu bot de Telegram.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Este es el comando de ayuda.')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'hola' in update.message.text.lower():
        await update.message.reply_text("¡Hola! ¿En qué puedo ayudarte hoy?")

# Iniciar bot
async def init_bot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    webhook_url = os.getenv("WEBHOOK_URL") + "/webhook/telegram"
    await application.bot.set_webhook(webhook_url)

    print(f"🚀 Webhook de Telegram configurado en: {webhook_url}")

    return application

@app.route('/webhook/telegram', methods=['POST'])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return "ok"

if __name__ == '__main__':
    import asyncio
    bot_app = asyncio.run(init_bot())  # inicia el bot y configura webhook
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
