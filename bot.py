from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8578279513:AAEbcZzaFl3S8OTAtcINV1VGHuJLoORf1ho"

CANAL = "https://t.me/+eUUFOhzJSw44ZmM5"
WHATSAPP = "https://wa.me/5350755467"


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if args and args[0] == "catalogo":
        texto = (
            "👋 Bienvenido a NexoVentas Studio\n\n"
            "Veo que vienes desde el catálogo digital 🛍\n\n"
            "Aquí puedes ver todo lo que tenemos disponible."
        )
    else:
        texto = (
            "👋 Hola, bienvenido a NexoVentas Studio\n\n"
            "Explora nuestras opciones 👇"
        )

    keyboard = [
        [InlineKeyboardButton("🛍 Ver canal de ofertas", url=CANAL)],
        [InlineKeyboardButton("💬 Comprar por WhatsApp", url=WHATSAPP)],
    ]

    await update.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# MENSAJES NORMALES
# =========================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "hola" in text:
        await update.message.reply_text(
            "👋 Hola 👋\n\n"
            "Bienvenido a NexoVentas.\n"
            "Escribe /start para ver opciones."
        )
    else:
        await update.message.reply_text(
            "🤖 No entendí eso.\n"
            "Escribe /start para comenzar."
        )


# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Bot en ejecución...")
    app.run_polling()


if __name__ == "__main__":
    main()
