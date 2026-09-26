import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

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

# Render proporciona automáticamente la URL pública
# del Web Service mediante RENDER_EXTERNAL_URL.
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

PORT = int(os.getenv("PORT", "10000"))


# =========================
# HEALTH CHECK PARA RENDER
# =========================

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def iniciar_health_server():
    health_port = PORT + 1
    server = HTTPServer(
        ("0.0.0.0", health_port),
        HealthHandler
    )

    print(f"❤️ Health server en puerto {health_port}")

    server.serve_forever()



# =========================
# VALIDACIÓN
# =========================

if not TOKEN:
    raise RuntimeError(
        "Falta la variable de entorno BOT_TOKEN."
    )

if not RENDER_URL:
    print(
        "⚠️ RENDER_EXTERNAL_URL no está definida. "
        "El bot funcionará localmente solamente si se configura "
        "otra URL de webhook."
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

    # 🔴 RECHAZO
    if any(w in text for w in [
        "no me interesa",
        "no quiero",
        "no estoy interesado",
        "deja eso",
        "basta",
    ]):
        return "rechazo"

    # 🟡 INTERÉS
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

    # 👋 SALUDO
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
# RESPONDER INTELIGENTE
# =========================

async def responder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "📩 MENSAJE RECIBIDO:",
        update.message.text
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
# MAIN
# =========================

def main():

    if not RENDER_URL:

        print(
            "⚠️ No se encontró RENDER_EXTERNAL_URL."
        )

        print(
            "🤖 Ejecutando bot mediante polling "
            "para pruebas locales..."
        )

        app = (
            Application
            .builder()
            .token(TOKEN)
            .build()
        )

        app.add_handler(
            CommandHandler("start", start)
        )

        app.add_handler(
            CommandHandler("stats", stats)
        )

        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                responder
            )
        )

        app.run_polling()

        return

    # =========================
    # RENDER / WEBHOOK
    # =========================

    webhook_url = (
        f"{RENDER_URL}/telegram"
    )

    print(
        "🤖 Bot NexoVentas Studio iniciando..."
    )

    print(
        f"🌐 Webhook: {webhook_url}"
    )

    print(
        f"🔌 Puerto: {PORT}"
    )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("stats", stats)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            responder
        )
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
