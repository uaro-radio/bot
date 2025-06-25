import datetime
import json
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from tokenize import group

import telegram.constants
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberAdministrator, \
    ChatMemberOwner, InputMediaPhoto, ReplyKeyboardRemove
from telegram.constants import ChatMemberStatus
from telegram.ext import filters, Application, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, \
    ConversationHandler
from dotenv import load_dotenv
import datetime as dt

from bin.Inline_Keyboards import Inline_Keyboard
from bin.Logging import logging, Core_Log, SQLite_Log, ICS_Log, IBS_Log, SS_Log
from bin.Reply_Keyboards import Reply_Keyboard
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
InlineKeyboards = Inline_Keyboard()
ReplyKeyboards = Reply_Keyboard()

configs_channel_keys = ['main_command_channel', 'sell_channel', 'sell_channel_admin',
                        "conversation_with_admins_channel"]
for x in configs_channel_keys:
    if not "." in str(ConfigManager.get_value(x)):
        ConfigManager.set_value(x, "1.1")
        Core_Log.warning(f"CONFIG: В ключі {x} записана некоректна інформація!\n"
                         f"Записано стандартні значення!")

# Conversation handler stuff
sell_s,sell_s2 = range(2)
conv_with_adm_s = range



main_command_channel = ConfigManager.get_value("main_command_channel").split(".")
config_chat_id = main_command_channel[0]
config_msg_thread_id = main_command_channel[1]

thx_delay = int(ConfigManager.get_value("thx_delay"))

sell_channel = ConfigManager.get_value("sell_channel").split(".")
sell_channel_admin = ConfigManager.get_value("sell_channel_admin").split(".")

conversation_with_admins_channel = ConfigManager.get_value("conversation_with_admins_channel").split(".")
ICS_handler_filters = (filters.TEXT|filters.ATTACHMENT|filters.PHOTO|
                       filters.AUDIO|filters.COMMAND)

send_all_info_filters = (filters.Regex("💻 Сайт") | filters.Regex("⛪️ Instagram") | filters.Regex("🖥 Ютуб")
                         | filters.Regex("💳 Підтримати нас"))

delay_factor = int(ConfigManager.get_value("delay_start_factor")) # 0 (OFF) | 1 (ON)
delay_on_start = int(ConfigManager.get_value("delay_start_factor_time")) # IN SECONDS
async def Test_Handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    print(msg.message_thread_id)
    print(msg.photo)
    print(msg.reply_to_message.text)

async def set_channel_to_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    keys = '\n'.join(configs_channel_keys)
    if not " " in msg.text:
        await msg.reply_text("Відсутній ключ!\n"
                             f"Ключі: \n{keys}")
        return
    args = msg.text.split(" ")
    if msg.message_thread_id:
        if args[1] in configs_channel_keys:
            ConfigManager.set_value(args[1], f"{chat.id}.{msg.message_thread_id}")
            await msg.reply_text(f"Успішно встановлено {args[1]}")
    else:
        await msg.reply_text('Виникла помилка!\n Канал не є гілкою!\n Перевір логи')
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
    global main_command_channel, config_chat_id, config_msg_thread_id, \
        thx_delay, sell_channel, sell_channel_admin,\
        conversation_with_admins_channel
    main_command_channel = ConfigManager.get_value("main_command_channel").split(".")
    config_chat_id = main_command_channel[0]
    config_msg_thread_id = main_command_channel[1]
    thx_delay = int(ConfigManager.get_value("thx_delay"))
    sell_channel = ConfigManager.get_value("sell_channel").split(".")
    conversation_with_admins_channel = ConfigManager.get_value("conversation_with_admins_channel").split(".")
    sell_channel_admin = ConfigManager.get_value("sell_channel_admin").split(".")
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
        is_linked = linked_forum_chats.get_linked(chat.id, msg.message_thread_id)
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

async def sell_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    await msg.reply_text("Оголошення скасовано")
    return ConversationHandler.END
async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return ConversationHandler.END
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    await msg.reply_text(msg_content.sell_start_message, reply_markup=Inline_Keyboard.cancel_keyboard)
    await msg.reply_photo(Path("Data/Examples/Sell_example.jpg"))
    await msg.reply_text(msg_content.sell_start_message_2, reply_markup=ReplyKeyboardRemove())
    context.user_data['photo_0'] = ''
    context.user_data['photo_1'] = ''
    context.user_data['photo_2'] = ''
    context.user_data['photo_3'] = ''
    context.user_data['photo_4'] = ''
    context.user_data['counter'] = 0
    return sell_s

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    """username = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@"+str(user.username)
    additional_info_text = f"Користувач: {user.id}/{username}\n"
    try:
        await context.bot.send_photo(chat_id=sell_channel_admin[0], message_thread_id=sell_channel_admin[1],
                                     reply_markup=InlineKeyboards.SS_to_admin(user.id, msg.id),
                                     photo=msg.photo, caption=additional_info_text+msg.caption)
        await msg.reply_text("Оголошення успішно надіслано на перевірку, очікуйте результату")
    except Exception as e:
        await msg.reply_text("Виникла помилка при створені оголошення, зв'яжіться з адміністрацією")
        SS_Log.error(e)
    return ConversationHandler.END"""
    description_text = 'Тепер надішліть ТІЛЬКИ ОПИС оголошення:'
    if msg.text and msg.text.startswith("/done"):
        await chat.send_message(description_text)
        return sell_s2
    elif msg.text:
        await msg.reply_text("Попробуйте ще раз")
        return sell_s

    if context.user_data['counter'] < 4:
        context.user_data[f'photo_{context.user_data["counter"]}'] = msg.photo[-1].file_id
        context.user_data['counter'] = context.user_data['counter']+1
        await chat.send_message(f"Ви ще можете надіслати {5-context.user_data['counter']} фото.\n"
                                f"Якщо більше не бажаєте надсилати фото, введіть /done")
        return sell_s
    else:
        context.user_data[f'photo_{context.user_data["counter"]}'] = msg.photo[-1].file_id
        await chat.send_message("Досягнуто максимальної кількості фото!")
        await chat.send_message(description_text)
        return sell_s2
async def sell_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    media_collection = []
    for x in range(context.user_data["counter"]):
        media_collection.append(InputMediaPhoto(media=context.user_data[f"photo_{x}"]))
    username = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(user.username)
    markdown_seller_username = username if username.startswith(
        '@') else f'[{username}](tg://user?id={user.id})'
    additional_info_text = (f"Користувач: {user.id}/{markdown_seller_username}\n"
                            f"Опис:\n\n")
    context.user_data['sell_text'] = text_parser.get_clear_fullname(msg.text)
    context.user_data['seller_username'] = username


    try:
        await context.bot.send_media_group(chat_id=sell_channel_admin[0], message_thread_id=sell_channel_admin[1],
                                     media=media_collection)
        await context.bot.send_message(chat_id=sell_channel_admin[0], message_thread_id=sell_channel_admin[1],
                                       reply_markup=InlineKeyboards.SS_to_admin(user.id), text=additional_info_text + msg.text,
                                       parse_mode=telegram.constants.ParseMode.MARKDOWN)
        await msg.reply_text("Оголошення успішно надіслано на перевірку, очікуйте результату")
    except Exception as e:
        await msg.reply_text("Виникла помилка при створені оголошення, зв'яжіться з адміністрацією")
        SS_Log.error(e)
    return ConversationHandler.END
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
    placeholders = [["$USER$",text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(user.username)],
                    ["$REP$", user_analytics[4] if not user_analytics[4] is None else 0]]
    msg_profile = msg_content.placeholders_to_information(msg_profile, placeholders)
    await msg.reply_text(msg_profile, parse_mode=telegram.constants.ParseMode.HTML)


async def conversation_with_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return ConversationHandler.END
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    await chat.send_message(msg_content.conversation_with_admin_start,
                            reply_markup=ReplyKeyboards.cancel)
    return conv_with_adm_s
async def conversation_with_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    username = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(user.username)
    markdown_sender_username = username if username.startswith(
        '@') else f'[{username}](tg://user?id={user.id})'
    additional_info_text = (f"Користувач: {user.id}/{markdown_sender_username}\n"
                            f"\n\n")
    text = additional_info_text + text_parser.get_clear_fullname(msg.text)
    try:
        await context.bot.send_message(chat_id=conversation_with_admins_channel[0], message_thread_id=conversation_with_admins_channel[1],
                                       text=text,
                                       parse_mode=telegram.constants.ParseMode.MARKDOWN)
    except Exception as e:
        await msg.reply_text("Виникла помилка! Попробуйте ще раз або зверніться в чат UARO")
        Core_Log.error(e)
async def conversation_with_admin_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    if user.id == context.bot.id:
        return
    await chat.send_message("Чат з адміністрацією завершений!\n"
                            "Адміністрація всеодно зможе відповісти на ваші повідомлення.",
                            reply_markup=ReplyKeyboards.start)
    return ConversationHandler.END
async def conversation_with_admin_reply_handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if user.id == context.bot.id:
        return
    if not msg.message_thread_id:
        return
    if msg.reply_to_message.text:
        if chat.id == int(conversation_with_admins_channel[0]) \
                and msg.message_thread_id == int(conversation_with_admins_channel[1]) \
                and msg.reply_to_message.text.startswith("Користувач"):
            username = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(
                user.username)
            sender_id = msg.reply_to_message.text.split("\n")[0].replace("Користувач: ","")
            sender_id = sender_id.split("/")[0]
            markdown_adm_username = username if username.startswith(
                '@') else f'[{username}](tg://user?id={user.id})'
            text = (f"Відповідь адміністрації:\n\n"
                    f"{msg.text}\n\n"
                    f"Адміністратор: {markdown_adm_username}")
            await context.bot.send_message(chat_id=sender_id, text=text, parse_mode=telegram.constants.ParseMode.MARKDOWN)
"""async def send_solarvhf_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await msg.reply_photo(BytesIO(await hamqsl.get_hamqsl_solarpic_b()))"""
async def send_all_info_medium(update:Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return ConversationHandler.END
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    if not chat.type == "private":
        return
    await msg.reply_text("Яку інформацію бажаєте знати?")

async def send_all_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if delay_factor:
        current_time = time.time()
        elapsed_time = current_time - start_time
        delay = delay_on_start
        if not elapsed_time >= delay:
            Core_Log.warning(f"Ігнорування! (Skip commands on start) | e_time: {round(float(elapsed_time),2)}/{delay}")
            return ConversationHandler.END
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
    await msg.reply_text(msg_content.start_message, parse_mode=telegram.constants.ParseMode.HTML,
                         reply_markup=ReplyKeyboards.start)
    try:
        return ConversationHandler.END
    except:
        pass

async def Callback_Query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query = update.callback_query
    chat = query.message.chat
    message = query.message
    qd = query.data
    args = qd.split("_")
    """if qd.startswith("unmute_"):
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
"""
    Core_Log.info(f"CQ: {user.username}/{qd}")
    username = text_parser.get_clear_fullname(user.full_name) if user.username is None else "@" + str(user.username)
    if args[0] == "sell-accept":
        markdown_username = username if username.startswith('@') else f'[{username}](tg://user?id={user.id})'
        seller_username = context.user_data["seller_username"]
        markdown_seller_username = seller_username if seller_username.startswith('@') else f'[{seller_username}](tg://user?id={args[1]})'
        edited_text = (f"Користувач: {args[1]}/{markdown_seller_username}\n"
                        f"Опис:\n\n"
                        f"{context.user_data['sell_text']}\n\n"
                       f"Одобрено: {markdown_username}")

        media_collection = []
        sell_text = (f"Продавець: "
         f"{markdown_seller_username}\n\n"
                     f"{context.user_data['sell_text']}")
        for x in range(context.user_data["counter"]):
            media_collection.append(InputMediaPhoto(media=context.user_data[f"photo_{x}"],
            caption=sell_text if x == 0 else None, parse_mode=telegram.constants.ParseMode.MARKDOWN if x == 0 else None))
        try:
            await context.bot.send_media_group(chat_id=int(sell_channel[0]), message_thread_id=int(sell_channel[1]),
                            media=media_collection)
            await context.bot.edit_message_text(edited_text, chat.id, message.message_id, parse_mode=telegram.constants.ParseMode.MARKDOWN)
            await context.bot.send_message(args[1], msg_content.sell_accept(markdown_seller_username),
                                           parse_mode=telegram.constants.ParseMode.MARKDOWN)
        except Exception as e:
            Core_Log.error(e)
            await chat.send_message("Помилка! Перевір логи!")
        context.user_data.clear()
    if args[0] == "sell-deny":
        seller_username = context.user_data['seller_username']
        markdown_username = username if username.startswith('@') else f'[{username}](tg://user?id={user.id})'
        markdown_seller_username = seller_username if seller_username.startswith(
            '@') else f'[{seller_username}](tg://user?id={args[1]})'
        edited_text = (f"Користувач: {args[1]}/{markdown_seller_username}\n"
                        f"Опис:\n\n"
                        f"{context.user_data['sell_text']}\n\n"
                       f"Відхилено: {markdown_username}")
        try:
            await context.bot.edit_message_text(edited_text, chat.id, message.message_id, parse_mode=telegram.constants.ParseMode.MARKDOWN)
            await context.bot.send_message(args[1], msg_content.sell_deny(markdown_username), parse_mode=telegram.constants.ParseMode.MARKDOWN)
        except Exception as e:
            Core_Log.error(e)
            await chat.send_message("Помилка! Перевір логи!")
    if args[0] == "sell-cancel":
        await chat.send_message("Оголошення скасовано!", reply_markup=ReplyKeyboards.start)
        await context.bot.delete_message(chat.id, message.message_id)
        return ConversationHandler.END



    try: await query.answer()
    except: pass


# Conversaion Handlers
sell_conv = ConversationHandler(
        entry_points=[CommandHandler("sell", sell_start)],
        states={
            sell_s: [MessageHandler(~filters.Regex("❌ Скасувати"), callback=sell)],
            sell_s2: [MessageHandler(filters.TEXT, callback=sell_2)]
        },
        fallbacks=[MessageHandler(filters.Regex("❌ Скасувати"), callback=sell_back)],
    )
conv_with_adm_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("☎️ Зв'язок з адміністрацією")&filters.USER, conversation_with_admin_start)],
        states={
            conv_with_adm_s: [MessageHandler(~filters.Regex("❌ Скасувати"), callback=conversation_with_admin)],
        },
        fallbacks=[MessageHandler(filters.Regex("❌ Скасувати"), callback=conversation_with_admin_end)],
    )




def main():
    check_db()
    app = Application.builder().token(BOT_TOKEN).build()
    # Message Handlers
    #app.add_handler(MessageHandler(filters.ALL, Test_Handler), group=3)
    app.add_handler(MessageHandler(ICS_handler_filters, information_correction_system), group=1)
    app.add_handler(MessageHandler(ICS_handler_filters, information_backup_system), group=2)
    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT, conversation_with_admin_reply_handler), group=3)
    # ReplyKeyboard Message Handlers
    #app.add_handler(MessageHandler(filters.Regex("📋 Про нас"), send_all_info_medium)) IN FUTURE
    # Command Handlers
    app.add_handler(CommandHandler('sql', direct_dev_data))
    #app.add_handler(CommandHandler('solarvhf', send_solarvhf_photo))
    #app.add_handler(CommandHandler('solarpic', send_solarpic_photo))
    app.add_handler(CommandHandler("gen_link", generate_forum_link))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("setccfg", set_channel_to_config))
    app.add_handler(CommandHandler("reload_config", reload_config))
    app.add_handler(CommandHandler("start", start))
    # Conversation Handlers
    app.add_handler(sell_conv)
    app.add_handler(conv_with_adm_conv)
    app.add_handler(CallbackQueryHandler(Callback_Query))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


main()