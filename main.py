import os
import logging
from flask import Flask, request
import paypalrestsdk
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import asyncio
from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de PayPal
paypalrestsdk.configure({
    'mode': 'live',  # 'sandbox' para pruebas, 'live' para producción
    'client_id': os.getenv('PAYPAL_CLIENT_ID'),
    'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
})

# Inicializar el bot de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Configuración del bot para responder a comandos
def start(update: Update, context: CallbackContext):
    update.message.reply_text('¡Hola! Soy tu bot de Telegram.')

def help(update: Update, context: CallbackContext):
    update.message.reply_text('Este es el comando de ayuda.')

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if 'hola' in text:
        update.message.reply_text("¡Hola! ¿En qué puedo ayudarte hoy?")

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_str = request.get_data(as_text=True)
        payload = json_str
        signature = request.headers.get('Paypal-Transmission-Sig')
        webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')
        verify = paypalrestsdk.notifications.webhook_event.verify(
            signature, payload, webhook_id)
        
        if verify:
            event = paypalrestsdk.notifications.WebhookEvent.from_json(payload)
            # Aquí puedes agregar lo que desees hacer con el evento
            print(event)
        else:
            print("El evento no es válido.")
        return '', 200

# Agregar el manejador de comandos al bot
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

message_handler = MessageHandler(Filters.text, handle_message)
dispatcher.add_handler(message_handler)

# Función principal de ejecución del bot y la aplicación Flask
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

class FlaskApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.app = app
        super(FlaskApplication, self).__init__()

    def load(self):
        return self.app

    def load_config(self):
        config = self.config.from_mapping({
            "bind": f"0.0.0.0:{os.getenv('PORT', 5000)}",
            "workers": 1,
            "accesslog": "-",
            "errorlog": "-",
        })
        for key, value in iteritems(self.options):
            config[key] = value

# Arrancar el servidor en producción con Gunicorn
if __name__ == "__main__":
    # Arrancar el bot y Flask en diferentes hilos
    asyncio.run(run_flask())  # Ejecutar Flask como servidor de producción
    FlaskApplication(app).run()  # Usar Gunicorn para producción
