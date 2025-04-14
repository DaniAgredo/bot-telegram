import os
import json
import hmac
import hashlib
import logging
from telegram import Bot
from telegram.ext import Application
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import asyncio

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # ID de tu canal VIP
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

app = Flask(__name__)
bot = Bot(token=TOKEN)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validación de IPN de PayPal
def verify_paypal_ipn(data):
    """Verifica la IPN de PayPal utilizando el HMAC y la clave secreta"""
    expected_signature = hmac.new(
        PAYPAL_SECRET.encode('utf-8'), 
        data.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    return expected_signature == data['signature']

# Función para agregar al usuario al canal VIP
async def give_access_to_channel(user_id):
    """Agrega al usuario al canal VIP después de pago exitoso"""
    try:
        await bot.send_message(
            chat_id=user_id, 
            text=f"🎉 ¡Tu pago fue exitoso! Ahora tienes acceso al canal VIP. ¡Bienvenido! 🔥"
        )
        # Enviar mensaje al canal, si el usuario está en el canal
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"Un nuevo miembro ha pagado y ha recibido acceso: {user_id}"
        )
        logger.info(f"Acceso concedido al usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al dar acceso al canal: {e}")

# Endpoint del Webhook
@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """Recibe el webhook de PayPal y verifica el pago"""
    data = request.json
    logger.info(f"Datos recibidos del webhook: {json.dumps(data)}")

    if not data:
        return jsonify({"status": "error", "message": "Sin datos"}), 400
    
    # Verificar que el pago fue exitoso
    if data.get("payment_status") == "Completed":
        user_id = data.get("custom")  # Usar el campo "custom" para el ID de Telegram

        # Si se recibe el ID de Telegram, enviamos el mensaje de acceso al canal VIP
        if user_id:
            try:
                # Usar create_task para ejecutar la función asincrónica en Flask
                asyncio.create_task(give_access_to_channel(user_id))
                return jsonify({"status": "success", "message": "Pago validado y acceso otorgado"}), 200
            except Exception as e:
                logger.error(f"Error al dar acceso al canal VIP: {e}")
                return jsonify({"status": "error", "message": "Error al dar acceso"}), 500
        else:
            return jsonify({"status": "error", "message": "ID de usuario no encontrado"}), 400
    else:
        return jsonify({"status": "error", "message": "Pago no completado"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
