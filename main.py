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

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Usar las variables de entorno para los tokens y claves
TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token de Telegram
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # ID del canal VIP de Telegram
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")  # Clave secreta de PayPal

# Configuración de Flask
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Configurar el logger para ver la salida de los eventos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para verificar la IPN de PayPal
def verify_paypal_ipn(data):
    """Verifica la IPN de PayPal utilizando HMAC y la clave secreta"""
    expected_signature = hmac.new(
        PAYPAL_SECRET.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return expected_signature == data['signature']

# Función para agregar al usuario al canal VIP después de pago
async def give_access_to_channel(user_id):
    """Envía mensaje al usuario y agrega acceso al canal VIP"""
    try:
        # Enviar mensaje de bienvenida al usuario que pagó
        await bot.send_message(
            chat_id=user_id,
            text="🎉 ¡Tu pago fue exitoso! Ahora tienes acceso al canal VIP. ¡Bienvenido! 🔥"
        )
        # Enviar notificación al canal de Telegram
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"Un nuevo miembro ha pagado y ha recibido acceso: {user_id}"
        )
        logger.info(f"Acceso concedido al usuario {user_id}")
    except Exception as e:
        logger.error(f"Error al dar acceso al canal: {e}")

# Endpoint para recibir el webhook de PayPal
@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """Recibe y maneja el webhook de PayPal para verificar pagos"""
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
                # Ejecutar la tarea asincrónica para conceder el acceso al canal VIP
                asyncio.run(give_access_to_channel(user_id))
                return jsonify({"status": "success", "message": "Pago validado y acceso otorgado"}), 200
            except Exception as e:
                logger.error(f"Error al dar acceso al canal VIP: {e}")
                return jsonify({"status": "error", "message": "Error al dar acceso"}), 500
        else:
            return jsonify({"status": "error", "message": "ID de usuario no encontrado"}), 400
    else:
        return jsonify({"status": "error", "message": "Pago no completado"}), 400

if __name__ == "__main__":
    # Iniciar el servidor Flask
    app.run(host="0.0.0.0", port=5000, debug=False)
