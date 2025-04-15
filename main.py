import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from fastapi import FastAPI
import uvicorn

PORT = int(os.getenv("PORT", "8000"))
TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot listo para ayudarte.")

async def contact_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aquí estoy, hablemos...")

# Inicializar bot
telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^hablar conmigo$"), contact_me))

@app.on_event("startup")
async def startup():
    # Establecer webhook
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    print(f"Webhook configurado en: {webhook_url}")

@app.post("/webhook")
async def telegram_webhook(update: dict):
    update = Update.de_json(update, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
