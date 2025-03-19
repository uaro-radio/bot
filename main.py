import datetime
import json
import os
import sys
import time
from io import BytesIO

import telegram.constants
from telegram import Update, ChatPermissions
from telegram.ext import filters, Application, ContextTypes, MessageHandler, CommandHandler
from dotenv import load_dotenv
import datetime as dt

from bin.Logging import logging, Core_Log, SQLite_Log, ICS_Log
from bin.SQL_func import init_user, is_user_exist, get_user, update_user_username, update_user_fullname, \
    get_user_by_username
from bin.SQLite_Driver import DataBase
from bin.func import check_db
from bin.func import hamqsl, text_parser
from bin.msgs_content import MessagesText

logging.getLogger("httpx").setLevel(logging.ERROR)

#Updater
Core_Log.info("Запит на оновлення...")
#os.system("git pull")


# .env check up
if not os.path.exists(".env"):
    Core_Log.critical(".env Файл не знайдено! Запуск неможливий!")
    sys.exit()

# Завантаження .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
start_time = time.time()

DataBase = DataBase()
hamqsl = hamqsl()
msg_content = MessagesText()
text_parser = text_parser()


ICS_handler_filters = (filters.TEXT|filters.ATTACHMENT|filters.PHOTO|
                       filters.AUDIO|filters.COMMAND)

mute_permissions = ChatPermissions(
    can_send_photos=False,
    can_send_polls=False,
    can_send_messages=False,
    can_send_audios=False,
    can_send_videos=False,
    can_send_documents=False,
    can_send_other_messages=False,
    can_send_video_notes=False,
    can_send_voice_notes=False
)
normal_permissions = ChatPermissions(
    can_send_photos=True,
    can_send_polls=True,
    can_send_messages=True,
    can_send_audios=True,
    can_send_videos=True,
    can_send_documents=True,
    can_send_other_messages=True,
    can_send_video_notes=True,
    can_send_voice_notes=True
)


delay_factor = 1 # 0 (OFF) | 1 (ON)
delay_on_start = 15 # IN SECONDS

async def direct_dev_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    if update.effective_user.id == 1459969627:
        print(update.effective_message.text)
        msg = update.effective_message.text.replace("/sql ", "")
        print(msg)
        a = DataBase.sendDirectSQL(msg)
        await update.effective_message.reply_text(a)
async def information_correction_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            ICS_Log.warning(f"Ігнорування! (Skip ICS on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    muted_chat_member = await context.bot.get_chat_member(chat.id, user.id)
    print(muted_chat_member)
    # ICS Nick
    if not is_user_exist(chat.id, user.id):
        if user.username is None:
            init_user(chat.id, user.id, '', user.full_name)
            ICS_Log.info(f"Зареєстровано користувача - ({chat.id}, {user.id}) {user.full_name}")
        else:
            init_user(chat.id, user.id, user.username)
            ICS_Log.info(f"Зареєстровано користувача - ({chat.id}, {user.id}) @{user.username}")
    else:
        db_user = get_user(chat.id, user.id)
        if not user.username is None:
            if not db_user[3] == '':
                update_user_fullname(chat.id, user.id, "")
                ICS_Log.info(f"Оновлення(Заміна, full_name del) ({chat.id}, {user.id}) @{user.username})")
            if not db_user[2] == user.username:
                update_user_username(chat.id, user.id, user.username)
                ICS_Log.info(f"Оновлення(Заміна username, несхожість) ({chat.id}, {user.id}) @{user.username})")
        else:
            if not db_user[2] == '':
                update_user_username(chat.id, user.id, "")
                ICS_Log.info(f"Оновлення(Заміна, username del) ({chat.id}, {user.id}) {user.full_name})")
            if not db_user[3] == user.full_name:
                update_user_fullname(chat.id, user.id, user.full_name)
                ICS_Log.info(f"Оновлення(Заміна full_name, несхожість) ({chat.id}, {user.id}) {user.full_name})")
    # /ICS-Nick

async def send_solarvhf_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    await msg.reply_photo(BytesIO(await hamqsl.get_hamqsl_solarvhf_b()))
async def send_solarpic_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    await msg.reply_photo(BytesIO(await hamqsl.get_hamqsl_solarpic_b()))

async def send_iss_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    iss_position = await hamqsl.get_iss_position()
    #print(iss_position)
    iss_position_json = json.loads(iss_position)
    a = await msg.reply_location(latitude=iss_position_json['iss_position']['latitude'], longitude=iss_position_json['iss_position']['longitude'])
    await a.reply_text(f"https://www.google.com/maps?q={iss_position_json['iss_position']['latitude']},{iss_position_json['iss_position']['longitude']}\n"
                       f"Час: {dt.datetime.fromtimestamp(iss_position_json['timestamp']).strftime('%H:%M:%S %d/%m/%y')}\n"
                       f"{"@"+user.username if not user.username is None else user.full_name}", disable_web_page_preview=True)

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    chat_member = await context.bot.get_chat_member(chat.id, user.id)
    if not chat_member.status in ['administrator', 'creator']:
        return
    args_User_name, args_datetime = text_parser.parse_mute_command(msg.text)

    if msg.reply_to_message:
        muted_user = msg.reply_to_message.from_user
        muted_user_id = muted_user.id
    else:
        if args_User_name is None:
            await msg.reply_text(msg_content.incorrect_command)
            return
        else:
            muted_user = get_user_by_username(chat.id, args_User_name.replace("@", ''))
            if len(muted_user) == 0:
                await msg.reply_text(msg_content.user_not_found)
                return
            else:
                muted_user_id = muted_user[1]

    if muted_user_id == context.bot.id or muted_user_id == user.id:
        return
    if msg.reply_to_message:
        if msg.reply_to_message.from_user.username is None:
            muted_user_name = text_parser.get_clear_fullname(muted_user.full_name)
        else:
            muted_user_name = f"@{muted_user.username}"
    else:
        muted_user_name = args_User_name
    admin_user = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@"+str(user.username)
    placeholders_replace = [["$USER$", muted_user_name], ["$EXP_DATE$", args_datetime.strftime('%H:%M:%S %d/%m/%y') if not args_datetime is None else "Вічність"], ["$ADMIN_NAME$", admin_user]]
    msg_text = msg_content.mute_command_message
    msg_text = msg_content.placeholders_to_information(msg_text, placeholders_replace)
    await msg.reply_text(msg_text, parse_mode=telegram.constants.ParseMode.HTML)
    if not args_datetime is None:
        await context.bot.restrict_chat_member(chat.id, muted_user_id, permissions=mute_permissions, until_date=args_datetime)
    else:
        await context.bot.restrict_chat_member(chat.id, muted_user_id, permissions=mute_permissions)

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    chat_member = await context.bot.get_chat_member(chat.id, user.id)

    if not chat_member.status in ['administrator', 'creator']:
        return
    if msg.reply_to_message:
        args_user_id = msg.reply_to_message.from_user.id
        muted_user_id = args_user_id
        muted_user_name = "@"+msg.reply_to_message.from_user.username if not msg.reply_to_message.from_user.username is None else msg.reply_to_message.from_user.full_name
    else:
        muted_user = get_user_by_username(chat.id, msg.text.strip("/unmute ").replace("@", ''))
        if len(muted_user) == 0 or not muted_user:
            await msg.reply_text(msg_content.user_not_found)
            return
        else:
            muted_user_id = muted_user[1]
            muted_user_name = muted_user[2]
    admin_user = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(user.username)
    placeholders_replace = [["$USER$", muted_user_name],["$ADMIN_NAME$", admin_user]]
    msg_text = msg_content.unmute_command_message
    msg_text = msg_content.placeholders_to_information(msg_text, placeholders_replace)
    muted_chat_member = await context.bot.get_chat_member(chat.id, muted_user_id)
    #default_chat_permissions = (await context.bot.get_chat(chat.id)).permissions
    if not muted_chat_member.status == "restricted":
        await msg.reply_text(msg_content.user_dont_muted)
        return
    await msg.reply_text(msg_text, parse_mode=telegram.constants.ParseMode.HTML)
    await context.bot.promote_chat_member(chat.id, muted_user_id)



def main():
    check_db()
    app = Application.builder().token(BOT_TOKEN).build()
    # Обробник повідомлень
    app.add_handler(MessageHandler(ICS_handler_filters, information_correction_system), group=1)
    # Command Handlers
    app.add_handler(CommandHandler('sql', direct_dev_data))
    app.add_handler(CommandHandler('solarvhf', send_solarvhf_photo))
    app.add_handler(CommandHandler('solarpic', send_solarpic_photo))
    app.add_handler(CommandHandler('iss', send_iss_position))
    app.add_handler(CommandHandler('mute', mute_command))
    app.add_handler(CommandHandler('unmute', unmute_command))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


main()