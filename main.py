import os
import json
import logging
import asyncio
from telegram import Bot
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

app = Flask(__name__)
bot = Bot(token=TOKEN)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para enviar mensajes de acceso al canal
async def give_access_to_channel(user_id):
    try:
        await bot.send_message(
            chat_id=user_id,
            text="🎉 ¡Tu pago fue exitoso! Ahora tienes acceso al canal VIP. 🔥"
        )
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"💸 Nuevo miembro confirmado: {user_id}"
        )
        logger.info(f"Acceso concedido a {user_id}")
    except Exception as e:
        logger.error(f"Error al dar acceso: {e}")

# Webhook para pagos de PayPal
@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    data = request.json
    logger.info(f"Webhook recibido: {json.dumps(data)}")

    if not data:
        return jsonify({"status": "error", "message": "Sin datos"}), 400

    if data.get("payment_status") == "Completed":
        user_id = data.get("custom")
        if user_id:
            try:
                asyncio.run(give_access_to_channel(user_id))
                return jsonify({"status": "ok", "message": "Acceso otorgado"}), 200
            except Exception as e:
                logger.error(f"Error: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "error", "message": "Falta user_id"}), 400
    else:
        return jsonify({"status": "error", "message": "Pago no completado"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
