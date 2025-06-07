import datetime
import json
import os
import sys
import time
from io import BytesIO
from tokenize import group

import telegram.constants
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberAdministrator, \
    ChatMemberOwner
from telegram.constants import ChatMemberStatus
from telegram.ext import filters, Application, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import datetime as dt

from bin.Logging import logging, Core_Log, SQLite_Log, ICS_Log, IBS_Log
from bin.SQL_func import init_user, is_user_exist, get_user, update_user_username, update_user_fullname, \
    get_user_by_username, init_analytics_user, get_user_analytics, update_analytics_msg_count, update_analytics_thx_count, \
    update_analytics_thx_count
from bin.SQLite_Driver import DataBase
from bin.func import check_db
from bin.func import hamqsl, text_parser, back_up_messages, linked_forum_chats, DelayAction, ConfigManager
from bin.msgs_content import MessagesText

logging.getLogger("httpx").setLevel(logging.ERROR)
Core_Log.info("\n\nСтарт логу")
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
back_up_messages = back_up_messages()
linked_forum_chats = linked_forum_chats()
DelayAction = DelayAction()
ConfigManager = ConfigManager()

if not "." in ConfigManager.get_value("main_command_channel"):
    Core_Log.error("Перевір конфіг!")
    sys.exit()

main_command_channel = ConfigManager.get_value("main_command_channel").split(".")
config_chat_id = main_command_channel[0]
config_msg_thread_id = main_command_channel[1]
thx_delay = int(ConfigManager.get_value("thx_delay"))
ICS_handler_filters = (filters.TEXT|filters.ATTACHMENT|filters.PHOTO|
                       filters.AUDIO|filters.COMMAND)

delay_factor = int(ConfigManager.get_value("delay_start_factor")) # 0 (OFF) | 1 (ON)
delay_on_start = int(ConfigManager.get_value("delay_start_factor_time")) # IN SECONDS
async def Test_Handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    print(msg.message_thread_id)


async def set_main_command_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not update.effective_user.id == 1459969627:
        return
    if msg.message_thread_id:
        ConfigManager.set_value("main_command_channel", f"{chat.id}.{msg.message_thread_id}")
        await msg.reply_text("Успішно встановлено main_command_channel")
    else:
        await msg.reply_text('Виникла помилка! Перевір логи')
async def reload_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not update.effective_user.id == 1459969627:
        return
    global main_command_channel, config_chat_id, config_msg_thread_id, thx_delay
    main_command_channel = ConfigManager.get_value("main_command_channel").split(".")
    config_chat_id = main_command_channel[0]
    config_msg_thread_id = main_command_channel[1]
    thx_delay = int(ConfigManager.get_value("thx_delay"))
    await msg.reply_text("Конфіг успішно перезавантажено")

async def generate_forum_link(update:Update, context: ContextTypes.DEFAULT_TYPE):
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
    status = await context.bot.get_chat_member(chat.id, user.id)
    if status.status == (ChatMemberStatus.ADMINISTRATOR or ChatMemberStatus.OWNER) or status.status =="creator":
        if not " " in msg.text or len(msg.text.split(" ")[1]) <3:
                return await msg.reply_text("Некоректне використання команди, назва зв'язку має бути не менше 3\n\n"
                                            "Приклад використання: /gen_link НАЗВА")
        if msg.message_thread_id is None:
            return await msg.reply_text("Ви не можете ініціалізувати зв'язок в загальному чаті! Використайте інший чат для зв'язку")
        link_name = msg.text.split(" ")[1]
        all_links_by_name = linked_forum_chats.get_links_by_name(link_name)
        print(all_links_by_name)
        if len(all_links_by_name) == 0:
            linked_forum_chats.create_link(chat.id, msg.message_thread_id, link_name)
            await msg.reply_text("Зв'язок ініціалізовано!\n"
                                 f"Назва зв'язку: {link_name}\n"
                                 f"Схема: {chat.id},{msg.message_thread_id} -> ?,?")
        else:
            if all_links_by_name[0][5] == link_name and all_links_by_name[0][1] == chat.id:
                is_linked = linked_forum_chats.get_linked(chat.id, msg.message_thread_id)[0]
                if is_linked:
                    return await msg.reply_text("В цьому каналі вже є існуючий зв'язок з цією назвою:\n"
                                                f"Назва: {is_linked[5]}\n"
                                                f"Схема: {chat.id},{msg.message_thread_id} -> {is_linked[2]},{is_linked[4]}")
                return await msg.reply_text("Зв'язок вже ініціалізовано!\n"
                                            "Використайте команду в іншому чаті для зв'язування."
                                            f"Назва зв'язку: {link_name}\n"
                                            f"Схема: {chat.id},{msg.message_thread_id} -> ?,?")
            else:
                linked_forum_chats.update_link_to_chat_and_to_thread_by_name(chat.id, msg.message_thread_id, link_name)
                return await msg.reply_text("Зв'язок створено!\n"
                                            f"Назва зв'язку: {link_name}\n"
                                            f"Схема: {all_links_by_name[0][1]},{all_links_by_name[0][3]} -> {chat.id},{msg.message_thread_id}")
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
    # ICS Nick
    if not is_user_exist(chat.id, user.id):
        if user.username is None:
            init_user(chat.id, user.id, '', user.full_name)
            ICS_Log.info(f"Зареєстровано користувача - ({chat.id}, {user.id}) {user.full_name}")
        else:
            init_user(chat.id, user.id, user.username)
            ICS_Log.info(f"Зареєстровано користувача - ({chat.id}, {user.id}) @{user.username}")
        init_analytics_user(chat.id, user.id)
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
        # ICS Analytics
        user_analytics = get_user_analytics(chat.id, user.id)
        user_msg_count = user_analytics[5]
        if user_msg_count is None:
            update_analytics_msg_count(chat.id, user.id)
        else:
            update_analytics_msg_count(chat.id, user.id,int(user_msg_count)+1)
    # ICS thx
    if msg.reply_to_message and not msg.reply_to_message.from_user.id == context.bot.id and ("👍" or "👎") in msg.text:
        if DelayAction.get_by_name("rep"):
            if not DelayAction.is_ready("rep"):
                text_delay = str(int(thx_delay))+" секунд" if thx_delay<60 else str(int(thx_delay/60)) +" хвилин"
                return await msg.reply_text(f"Ви можете змінювати репутацію користувачів не частіше ніж раз в {text_delay}")
        if user.id == msg.reply_to_message.from_user.id:
            return
        if msg.reply_to_message and msg.text and msg.text == "👍":
            user_reply_to_message = get_user_analytics(chat.id, msg.reply_to_message.from_user.id)
            username_reply_to_message = text_parser.get_clear_fullname(msg.reply_to_message.from_user.full_name) if msg.reply_to_message.from_user.username is None else "@" + str(msg.reply_to_message.from_user.username)
            if user_reply_to_message:
                user_thx_count = user_reply_to_message[4]
                if user_thx_count is None:
                    update_analytics_thx_count(chat.id, msg.reply_to_message.from_user.id,1)
                    await msg.reply_text(f"Ви підвищили репутацію користувача {username_reply_to_message} на 1\n"
                                         f"Репутація: 1")

                else:
                    update_analytics_thx_count(chat.id, msg.reply_to_message.from_user.id, int(user_thx_count)+1)
                    await msg.reply_text(f"Ви підвищили репутацію користувача {username_reply_to_message} на 1\n"
                                         f"Репутація: {int(user_thx_count)+1}")
                DelayAction.add_delay_action("rep", datetime.datetime.now(), thx_delay)
            else:
                await msg.reply_text(f"Неможливо підвищити репутацію користувача {username_reply_to_message}\n"
                                     f"Він мусить надіслати хоч одне повідомлення")
        elif msg.reply_to_message and msg.text and msg.text == "👎":
            user_reply_to_message = get_user_analytics(chat.id, msg.reply_to_message.from_user.id)
            username_reply_to_message = text_parser.get_clear_fullname(msg.reply_to_message.from_user.full_name) if msg.reply_to_message.from_user.username is None else "@" + str(msg.reply_to_message.from_user.username)
            if user_reply_to_message:
                user_thx_count = user_reply_to_message[4]
                if user_thx_count is None:
                    update_analytics_thx_count(chat.id, msg.reply_to_message.from_user.id,-1)
                    await msg.reply_text(f"Ви понизили репутацію користувача {username_reply_to_message} на 1\n"
                                         f"Репутація: -1")
                else:
                    update_analytics_thx_count(chat.id, msg.reply_to_message.from_user.id, int(user_thx_count)-1)
                    await msg.reply_text(f"Ви понизили репутацію користувача {username_reply_to_message} на 1\n"
                                         f"Репутація: {int(user_thx_count)-1}")
                DelayAction.add_delay_action("rep", datetime.datetime.now(), thx_delay)
            else:
                await msg.reply_text(f"Неможливо підвищити репутацію користувача {username_reply_to_message}\n"
                                     f"Він мусить надіслати хоч одне повідомлення")
async def information_backup_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    message_tags = text_parser.get_message_content_types(msg)
    if message_tags["text"]:
        information = msg.text
        if information.startswith("/"):
            return
    else:
        information = "Нетекстова інформвція"
    tags = [k for k, v in message_tags.items() if v == 1]
    username_changed = user.username + "/" + str(user.id) if user.username is not None else str(
        user.full_name) + "/" + str(user.id)
    if not msg.edit_date:
        IBS_Log.info(f"Повідомлення, користувач {username_changed}\n"
                     f"Вміст: {information}\n"
                     f"Теги: {tags}\n")
        await back_up_messages.add_message_to_db(msg, chat.id, user.id, msg.id,context)
        print(f"{chat.id}, {msg.message_thread_id}")
        is_linked = linked_forum_chats.get_linked(chat.id, msg.message_thread_id)
        print(is_linked)
        if is_linked:
            try:
                await msg.forward(chat_id=is_linked[0][2], message_thread_id=is_linked[0][4])
            except Exception as e:
                user_msg = {msg.text if not msg.text is None else f"Перевір логи! Нетекстове повідомлення!\nТеги: {text_parser.get_message_content_types(msg)}"}
                exception_message = ("Помилка пересилання повідомлення!\n"
                                     f"Користувач: {user.id}/{user.username}/{user.full_name}\n"
                                     f"Повідомлення: {user_msg}\n")
                await context.bot.send_message(chat_id=is_linked[0][2],text=exception_message)
                IBS_Log.error(f"Помилка!\n\n{e}")

    else:
        IBS_Log.info(f"Повідомлення, користувач {username_changed}\n"
                     f"Вміст: {information}\n"
                     f"Теги: {tags}\n"
                     f"РЕДАГОВАНО")
        await back_up_messages.add_changed_message_to_db(msg, chat.id, user.id, msg.id,context)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    global config_chat_id
    global config_msg_thread_id
    if not chat.type == "private" and not (msg.message_thread_id and int(config_chat_id) == chat.id and int(config_msg_thread_id) == msg.message_thread_id):
        return
    msg_profile = msg_content.profile_message
    user_analytics = get_user_analytics(chat.id, user.id)
    if not user_analytics:
        init_analytics_user(chat.id, user.id)
        user_analytics = get_user_analytics(chat.id, user.id)
    placeholders = [["$USER$",text_parser.get_clear_fullname(msg.reply_to_message.from_user.full_name) if msg.reply_to_message.from_user.username is None else "@" + str(msg.reply_to_message.from_user.username)],
                    ["$REP$", user_analytics[4] if not user_analytics[4] is None else 0]]
    msg_profile = msg_content.placeholders_to_information(msg_profile, placeholders)
    await msg.reply_text(msg_profile, parse_mode=telegram.constants.ParseMode.HTML)


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
    global config_chat_id
    global config_msg_thread_id
    if not chat.type == "private" and not (msg.message_thread_id and int(config_chat_id) == chat.id and int(config_msg_thread_id) == msg.message_thread_id):
        return
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
    global config_chat_id
    global config_msg_thread_id
    if not chat.type == "private" and not (msg.message_thread_id and int(config_chat_id) == chat.id and int(config_msg_thread_id) == msg.message_thread_id):
        return
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
    global config_chat_id
    global config_msg_thread_id
    if not chat.type == "private" and not (msg.message_thread_id and int(config_chat_id) == chat.id and int(config_msg_thread_id) == msg.message_thread_id):
        return
    iss_position = await hamqsl.get_iss_position()
    #print(iss_position)
    iss_position_json = json.loads(iss_position)
    a = await msg.reply_location(latitude=iss_position_json['iss_position']['latitude'], longitude=iss_position_json['iss_position']['longitude'])
    await a.reply_text(f"https://www.google.com/maps?q={iss_position_json['iss_position']['latitude']},{iss_position_json['iss_position']['longitude']}\n"
                       f"Час: {dt.datetime.fromtimestamp(iss_position_json['timestamp']).strftime('%H:%M:%S %d/%m/%y')}\n"
                       f"{'@'+user.username if not user.username is None else user.full_name}", disable_web_page_preview=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not chat.type == "private":
        return
    await msg.reply_text(msg_content.start_message, parse_mode=telegram.constants.ParseMode.HTML)


"""async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Зняти RO", callback_data=f"unmute_{user.id}_{muted_user_id}")]])

    await msg.reply_text(msg_text, parse_mode=telegram.constants.ParseMode.HTML, reply_markup=reply_markup)
    if not args_datetime is None:
        await context.bot.restrict_chat_member(chat.id, muted_user_id, permissions=mute_permissions, until_date=args_datetime)
    else:
        await context.bot.restrict_chat_member(chat.id, muted_user_id, permissions=mute_permissions)"""

"""async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await context.bot.promote_chat_member(chat.id, muted_user_id)"""

async def Callback_Query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat = query.message.chat
    message = query.message
    qd = query.data
    args = qd.split("_")
    if qd.startswith("unmute_"):
        chat_member = await context.bot.get_chat_member(chat.id, query.from_user.id)
        if not chat_member.status in ['administrator', 'creator']:
            await query.answer("Ви не адміністратор!")
            return
        name_user = get_user(chat.id,args[2])
        if name_user[2] == None or name_user[2] == "Null" or name_user[2] == '':
            name_user_finally = name_user[3]
        else:
            name_user_finally = name_user[2]
        admin_user = text_parser.get_clear_fullname(query.from_user.full_name) if query.from_user.username is None else "@" + str(
            user.username)
        placeholders_replace = [["$USER$", name_user_finally], ["$ADMIN_NAME$", admin_user]]
        msg_text = msg_content.unmute_command_message
        msg_text = msg_content.placeholders_to_information(msg_text, placeholders_replace)
        await context.bot.edit_message_text(msg_text,chat.id, query.message.message_id, parse_mode=telegram.constants.ParseMode.HTML)
        await context.bot.promote_chat_member(chat.id, name_user[1])
        await query.answer("Користувач виведено з RO")




    try: await query.answer()
    except: pass

def main():
    check_db()
    app = Application.builder().token(BOT_TOKEN).build()
    # Обробник повідомлень
    #app.add_handler(MessageHandler(filters.ALL, Test_Handler), group=3)
    app.add_handler(MessageHandler(ICS_handler_filters, information_correction_system), group=1)
    app.add_handler(MessageHandler(ICS_handler_filters, information_backup_system), group=2)
    # Command Handlers
    app.add_handler(CommandHandler('sql', direct_dev_data))
    app.add_handler(CommandHandler('solarvhf', send_solarvhf_photo))
    app.add_handler(CommandHandler('solarpic', send_solarpic_photo))
    app.add_handler(CommandHandler('iss', send_iss_position))
    #app.add_handler(CommandHandler('mute', mute_command))
    #app.add_handler(CommandHandler('unmute', unmute_command))
    app.add_handler(CommandHandler("gen_link", generate_forum_link))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("set_command_channel", set_main_command_channel))
    app.add_handler(CommandHandler("reload_config", reload_config))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(Callback_Query))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


main()