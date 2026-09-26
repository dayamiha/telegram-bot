import os

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import uvicorn


# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")

CANAL = os.getenv(
    "CANAL",
    "https://t.me/+eUUFOhzJSw44ZmM5"
)

WHATSAPP = os.getenv(
    "WHATSAPP",
    "https://wa.me/5352016762"
)

PORT = int(os.getenv("PORT", "10000"))

WEBHOOK_URL = (
    "https://telegram-bot-4-xqls.onrender.com/telegram"
)


# =========================
# VALIDACIÓN
# =========================

if not TOKEN:
    raise RuntimeError(
        "Falta la variable de entorno BOT_TOKEN."
    )


# =========================
# ESTADO GLOBAL SIMPLE
# =========================

analytics = {
    "leads": 0,
    "interesados": 0,
    "rechazos": 0,
}


# =========================
# INTENT DETECTOR
# =========================

def detectar_intencion(text: str):

    text = text.lower()

    # RECHAZO
    if any(w in text for w in [
        "no me interesa",
        "no quiero",
        "no estoy interesado",
        "deja eso",
        "basta",
    ]):
        return "rechazo"

    # INTERÉS
    if any(w in text for w in [
        "tienda",
        "catálogo",
        "catalogo",
        "app",
        "crear",
        "precio",
        "cómo funciona",
        "como funciona",
        "quiero",
    ]):
        return "interesado"

    # SALUDO
    if any(w in text for w in [
        "hola",
        "buenas",
        "hey",
        "saludos",
    ]):
        return "saludo"

    return "neutral"


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    args = context.args

    analytics["leads"] += 1

    if args and args[0] == "catalogo":

        texto = (
            "👋 Bienvenido a NexoVentas Studio\n\n"
            "🛍 Vienes desde un catálogo digital\n"
            "Te mostramos todo lo que puedes crear aquí."
        )

    else:

        texto = (
            "👋 Hola 👋\n\n"
            "🚀 Te ayudo a crear tu tienda virtual "
            "o catálogo digital automático.\n\n"
            "Escribe algo como:\n"
            "- quiero una tienda\n"
            "- cómo funciona\n"
            "- precio"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Ver canal de demos",
                url=CANAL
            )
        ],
        [
            InlineKeyboardButton(
                "💬 Hablar por WhatsApp",
                url=WHATSAPP
            )
        ],
    ]

    await update.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# RESPONDER
# =========================

async def responder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "📩 MENSAJE RECIBIDO:",
        update.message.text,
        flush=True
    )

    text = update.message.text

    intent = detectar_intencion(text)

    user_data = context.user_data

    score = user_data.get("score", 0)

    # =========================
    # RECHAZO
    # =========================

    if intent == "rechazo":

        analytics["rechazos"] += 1

        user_data["state"] = "rechazado"
        user_data["score"] = score - 5

        await update.message.reply_text(
            "👌 Perfecto, entendido.\n"
            "Si necesitas una tienda virtual "
            "en el futuro, aquí estaré."
        )

        return

    # Si ya rechazó → no insistir

    if user_data.get("state") == "rechazado":
        return

    # =========================
    # SALUDO
    # =========================

    if intent == "saludo":

        user_data["score"] = score + 1

        await update.message.reply_text(
            "👋 Hola 👋\n\n"
            "Soy NexoVentas Studio Bot.\n"
            "Te ayudo a crear tiendas virtuales "
            "automáticas.\n\n"
            "Escribe 'quiero una tienda' "
            "o 'precio'."
        )

        return

    # =========================
    # INTERESADO
    # =========================

    if intent == "interesado":

        analytics["interesados"] += 1

        user_data["state"] = "interesado"
        user_data["score"] = score + 2

        keyboard = [
            [
                InlineKeyboardButton(
                    "🛍 Ver demos",
                    url=CANAL
                )
            ],
            [
                InlineKeyboardButton(
                    "💬 Ir a WhatsApp",
                    url=WHATSAPP
                )
            ],
        ]

        await update.message.reply_text(
            "🔥 Perfecto 🔥\n\n"
            "Con NexoVentas Studio puedes crear:\n"
            "🛍 Catálogo digital\n"
            "📲 Tienda online\n"
            "🤖 Bot de ventas automático\n\n"
            "👉 Puedes ver un ejemplo "
            "o hablar directamente por WhatsApp.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return

    # =========================
    # NEUTRAL
    # =========================

    await update.message.reply_text(
        "🤖 Te explico rápido:\n\n"
        "NexoVentas Studio crea tiendas "
        "virtuales automáticas para negocios.\n"
        "Sin programar, sin complicaciones.\n\n"
        "💬 Escribe 'quiero una tienda' "
        "para más info."
    )


# =========================
# ESTADÍSTICAS
# =========================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📊 ESTADÍSTICAS\n\n"
        f"Leads: {analytics['leads']}\n"
        f"Interesados: {analytics['interesados']}\n"
        f"Rechazos: {analytics['rechazos']}"
    )


# =========================
# CREAR APLICACIÓN TELEGRAM
# =========================

bot_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)


bot_app.add_handler(
    CommandHandler("start", start)
)


bot_app.add_handler(
    CommandHandler("stats", stats)
)


bot_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        responder
    )
)


# =========================
# FASTAPI
# =========================

web_app = FastAPI()


# =========================
# INICIO DEL SERVIDOR
# =========================

@web_app.on_event("startup")
async def startup():

    print(
        "🤖 Bot NexoVentas Studio iniciando...",
        flush=True
    )

    await bot_app.initialize()
    await bot_app.start()

    print(
        f"🌐 Webhook: {WEBHOOK_URL}",
        flush=True
    )

    await bot_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True
    )

    print(
        f"❤️ Health: https://telegram-bot-4-xqls.onrender.com/health",
        flush=True
    )

    print(
        f"🔌 Puerto: {PORT}",
        flush=True
    )


# =========================
# CIERRE DEL SERVIDOR
# =========================

@web_app.on_event("shutdown")
async def shutdown():

    print(
        "🛑 Deteniendo bot...",
        flush=True
    )

    await bot_app.stop()
    await bot_app.shutdown()


# =========================
# HEALTH CHECK
# =========================

@web_app.get("/health")
async def health():

    return PlainTextResponse(
        "OK",
        status_code=200
    )


# =========================
# WEBHOOK TELEGRAM
# =========================

@web_app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()

    update = Update.de_json(
        data,
        bot_app.bot
    )

    await bot_app.process_update(update)

    return PlainTextResponse(
        "OK",
        status_code=200
    )


# =========================
# RAÍZ
# =========================

@web_app.get("/")
async def root():

    return PlainTextResponse(
        "NexoVentas Studio Bot activo",
        status_code=200
    )


# =========================
# EJECUTAR
# =========================

if __name__ == "__main__":

    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=PORT
    )
