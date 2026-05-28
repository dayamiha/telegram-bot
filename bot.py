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
TOKEN = "8578279513:AAEbcZzaFl3S8OTAtcINV1VGHuJLoORf1ho"

CANAL = "https://t.me/+eUUFOhzJSw44ZmM5"
WHATSAPP = "https://wa.me/5350755467"

# =========================
# ESTADO GLOBAL SIMPLE (puedes luego migrar a DB)
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

    # 🔴 RECHAZO (prioridad máxima)
    if any(w in text for w in [
        "no me interesa",
        "no quiero",
        "no estoy interesado",
        "deja eso",
        "basta"
    ]):
        return "rechazo"

    # 🟡 INTERÉS EN NEGOCIO
    if any(w in text for w in [
        "tienda",
        "catálogo",
        "catalogo",
        "app",
        "crear",
        "precio",
        "cómo funciona",
        "quiero"
    ]):
        return "interesado"

    # 👋 SALUDO
    if any(w in text for w in [
        "hola",
        "buenas",
        "hey",
        "saludos"
    ]):
        return "saludo"

    return "neutral"


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
            "🚀 Te ayudo a crear tu tienda virtual o catálogo digital automático.\n"
            "Escribe algo como:\n"
            "- quiero una tienda\n"
            "- cómo funciona\n"
            "- precio"
        )

    keyboard = [
        [InlineKeyboardButton("🛍 Ver canal de demos", url=CANAL)],
        [InlineKeyboardButton("💬 Hablar por WhatsApp", url=WHATSAPP)],
    ]

    await update.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# RESPONDER INTELIGENTE
# =========================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
            "Si necesitas una tienda virtual en el futuro, aquí estaré."
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
            "Te ayudo a crear tiendas virtuales automáticas.\n\n"
            "Escribe 'quiero una tienda' o 'precio'"
        )
        return

    # =========================
    # INTERESADO
    # =========================
    if intent == "interesado":

        analytics["interesados"] += 1
        user_data["state"] = "interesado"
        user_data["score"] = score + 2

        await update.message.reply_text(
            "🔥 Perfecto 🔥\n\n"
            "Con NexoVentas Studio puedes crear:\n"
            "🛍 Catálogo digital\n"
            "📲 Tienda online\n"
            "🤖 Bot de ventas automático\n\n"
            "👉 ¿Quieres ver un ejemplo o ir a WhatsApp?"
        )
        return

    # =========================
    # NEUTRAL (educación + conversión suave)
    # =========================
    await update.message.reply_text(
        "🤖 Te explico rápido:\n\n"
        "NexoVentas Studio crea tiendas virtuales automáticas para negocios.\n"
        "Sin programar, sin complicaciones.\n\n"
        "💬 Escribe 'quiero una tienda' para más info."
    )


# =========================
# DEBUG / ANALYTICS COMMAND
# =========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, responder)
    )

    print("🤖 Bot NexoVentas en ejecución...")
    app.run_polling()


if __name__ == "__main__":
    main()
