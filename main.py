import os
import logging
from flask import Flask, request
import paypalrestsdk
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from gunicorn.app.base import BaseApplication

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar PayPal
paypalrestsdk.configure({
    'mode': 'live',  # Cambia a 'sandbox' si estás probando
    'client_id': os.getenv('PAYPAL_CLIENT_ID'),
    'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
})

# Inicializar bot de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Configuración del bot para responder a comandos
def start(update: Update, context: CallbackContext):
    update.message.reply_text('¡Hola! Soy tu bot de Telegram.')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Este es el comando de ayuda.')

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if 'hola' in text:
        update.message.reply_text("¡Hola! ¿En qué puedo ayudarte hoy?")

# Crear aplicación Flask
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        payload = request.get_data(as_text=True)
        signature = request.headers.get('Paypal-Transmission-Sig')
        webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')

        verify = paypalrestsdk.notifications.webhook_event.verify(
            transmission_sig=signature,
            transmission_id=request.headers.get('Paypal-Transmission-Id'),
            transmission_time=request.headers.get('Paypal-Transmission-Time'),
            cert_url=request.headers.get('Paypal-Cert-Url'),
            auth_algo=request.headers.get('Paypal-Auth-Algo'),
            webhook_id=webhook_id,
            event_body=payload
        )

        if verify:
            event = paypalrestsdk.notifications.WebhookEvent.from_json(payload)
            print(f"✅ Evento recibido: {event.event_type}")
            # Aquí puedes manejar eventos de pago, etc.
        else:
            print("❌ El evento no es válido.")
        return '', 200

# Configurar bot de Telegram
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Clase para ejecutar Flask con Gunicorn
class FlaskApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.app = app
        super().__init__()

    def load(self):
        return self.app

    def load_config(self):
        config = {
            "bind": f"0.0.0.0:{os.getenv('PORT', '5000')}",
            "workers": 1,
            "accesslog": "-",
            "errorlog": "-"
        }
        for key, value in self.options.items():
            config[key] = value
        self.cfg.set_config(config)

# Ejecutar el bot y el servidor
if __name__ == "__main__":
    # Iniciar bot de Telegram
    updater.start_polling()
    print("✅ Bot de Telegram iniciado correctamente")

    # Iniciar servidor Flask con Gunicorn
    FlaskApplication(app).run()
