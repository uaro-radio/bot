import logging
import os

from telegram import Update
from telegram.ext import filters, Application, ContextTypes, MessageHandler
from dotenv import load_dotenv


# Завантаження .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Лог
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger("Core")
logging.getLogger("httpx").setLevel(logging.ERROR)

async def Message_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if user.is_bot: return
    print(f"MESSAGE:\n{chat.title}\n{user.full_name}\n{msg.text}")
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # Обробник повідомлень
    app.add_handler(MessageHandler(filters.ALL, Message_Handler), group=1)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


main()