import base64
import datetime
import os
import re
import ssl
import sys
from telegram.ext import ContextTypes
import telegram

from bin.Logging import SQLite_Log, Core_Log
from bin.SQL_func import init_message_user, init_changed_message_user
from bin.SQLite_Driver import DataBase
import datetime as dt
import aiohttp

db = DataBase()

def check_db():
    if not os.path.exists("Data.db"):
        Core_Log.warning("Файл бази даних не знайдено!")
        SQLite_Log.info("Створюю та ініцілізую базу даних...")
        try:
            db.GenerateNewDataBase()
            SQLite_Log.info("Успішно!")
        except Exception as e:
            SQLite_Log.critical("Помилка створення, перевір Exception")
            print(e)
            sys.exit()
    else:
        Core_Log.info("База даних - OK")



class hamqsl:
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    def __clear_old_hasql_solar(self): # In Future
        pass

    async def __get_fromURL_content_b(self, url:str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=self.ssl_context) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print("Не вдалося отримати зображення. Код помилки:", response.status)
                    return False

    """async def get_fromURL_content_b(self, url: str) -> bytes: # FOR DEBUG, DONT UNCOMMENT
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=self.ssl_context) as response:
                if response.status == 200:
                    self.__clear_old_hasql_solar()
                    return await response.read()
                else:
                    print("Не вдалося отримати. Код помилки:", response.status)"""
    async def get_hamqsl_solarvhf_b(self):
        url = "https://www.hamqsl.com/solarvhf.php"
        current_data = dt.datetime.now().strftime("%d-%m-%Y")
        if os.path.exists(f"Data/hamqsl_solar/solarvhf_{current_data}.png"):
            with open(f"Data/hamqsl_solar/solarvhf_{current_data}.png", "rb") as photo:
                photo_b = photo.read()
        else:
            with open(f"Data/hamqsl_solar/solarvhf_{current_data}.png", "wb") as file:
                photo_b = await self.__get_fromURL_content_b(url)
                file.write(photo_b)
        return photo_b
    async def get_hamqsl_solarpic_b(self):
        url = "https://www.hamqsl.com/solarpic.php"
        current_data = dt.datetime.now().strftime("%d-%m-%Y")
        if os.path.exists(f"Data/hamqsl_solar/solarpic_{current_data}.png"):
            with open(f"Data/hamqsl_solar/solarpic_{current_data}.png", "rb") as photo:
                photo_b = photo.read()
        else:
            with open(f"Data/hamqsl_solar/solarpic_{current_data}.png", "wb") as file:
                photo_b = await self.__get_fromURL_content_b(url)
                file.write(photo_b)
        return photo_b
    async def get_iss_position(self):
        url = "http://api.open-notify.org/iss-now.json"
        return (await self.__get_fromURL_content_b(url)).decode()
class text_parser:

    def parse_mute_command(self, text) -> tuple[str | None, dt.datetime | None]:
        pattern = r"/mute\s+(@\S+)?\s*(\d+)?\s*(доба|днів|день)?\s*(\d+)?\s*(година|годин|години)?\s*(\d+)?\s*(хв|хвилин|хвилини)?\s*(\d+)?\s*(секунд|секунди|сек)?"
        match = re.search(pattern, text)

        if not match:
            return None, None

        user = match.group(1) if match.group(1) else None

        # Перевірка на кількість днів (число) або відсутність
        days = int(match.group(2)) if match.group(2) else 0
        if match.group(3) and match.group(3) in ['доба', 'днів', 'день']:  # якщо є день/доба
            days = days if days else 1  # якщо не вказано число, ставимо 1

        hours = int(match.group(4)) if match.group(4) and match.group(5) else 0
        minutes = int(match.group(6)) if match.group(6) and match.group(7) else 0
        seconds = int(match.group(8)) if match.group(8) and match.group(9) else 0

        mute_duration = dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        dt_utc = dt.timezone(dt.timedelta(hours=2))
        mute_until = dt.datetime.now(dt_utc) + mute_duration
        if mute_duration.total_seconds() == 0:
            mute_until = None
        return user, mute_until


    def get_clear_fullname(self, fullname:str):
        bad_words = ["<b>", "<i>", "<code>", "<s>", "<u>", "<pre", "</b>", "</i>", "</code>", "</s>", "</u>", "</pre"]
        fullname = fullname
        for x in bad_words:
            fullname = fullname.replace(x, "")
        return fullname

    def get_message_content_types(self,message):
        return {
            "text": 1 if message.text else 0,
            "photo": 1 if message.photo else 0,
            "gif": 1 if message.animation else 0,  # Telegram позначає GIF як animation
            "video": 1 if message.video else 0,
            "voice": 1 if message.voice else 0,
            "audio": 1 if message.audio else 0,
            "document": 1 if message.document else 0,
            "sticker": 1 if message.sticker else 0,
            "video_note": 1 if message.video_note else 0,
            "dice": 1 if message.dice else 0,
            "poll": 1 if message.poll else 0,
            "location": 1 if message.location else 0,
            "contact": 1 if message.contact else 0,
            "game": 1 if message.game else 0
        }
class files_func:
    def __init__(self):
        self.datetime = datetime.datetime

    async def get_file_func(self, file_id: str, context: ContextTypes.DEFAULT_TYPE) -> str:
        try:
            # Отримати об'єкт файлу через context.bot
            tg_file = await context.bot.get_file(file_id)

            # Підготувати директорію для збереження
            save_dir = "Data/temp_files"
            os.makedirs(save_dir, exist_ok=True)

            # Отримати оригінальне ім'я файлу та розширення
            original_name = os.path.basename(tg_file.file_path)
            name, ext = os.path.splitext(original_name)

            # Додати мітку часу
            timestamp = self.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{name}_{timestamp}{ext}"
            full_path = os.path.join(save_dir, file_name)

            # Завантажити файл
            await tg_file.download_to_drive(custom_path=full_path)

            return full_path
        except Exception as e:
            print(f"[ERROR] get_file_func: {e}")
            return ""
class back_up_messages:
    def __init__(self):
        self.text_parser = text_parser()
        self.file_func = files_func()

    async def add_message_to_db(self, msg: telegram.Message, chat_id: int, user_id: int,msg_id:int, context: ContextTypes.DEFAULT_TYPE):
        try:
            text_parser = self.text_parser
            file_func = self.file_func

            content = text_parser.get_message_content_types(msg)
            its_text = content["text"]
            its_photo = content["photo"]
            its_gif = content["gif"]
            its_video = content["video"]
            information = ""

            if its_text:
                information = msg.text or ""

            elif its_photo and msg.photo:
                try:
                    photo = msg.photo[-1]  # найбільше фото — останнє
                    file_path = await file_func.get_file_func(photo.file_id, context)
                    with open(file_path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")
                    information = encoded
                except Exception as e:
                    information = f"not backupable information, tags: photo (error)"
                    its_photo = 0

            elif its_gif:
                information = "not backupable information, tags: gif"

            elif its_video:
                information = "not backupable information, tags: video"

            else:
                tags = [k for k, v in content.items() if v == 1]
                tag_text = ', '.join(tags) if tags else "none"
                information = f"not backupable information, tags: {tag_text}"

            return init_message_user(
                chat_id=chat_id,
                user_id=user_id,
                information=information,
                its_text=its_text,
                its_photo=its_photo,
                its_gif=its_gif,
                its_video=its_video,
                deleted=0,
                msg_id=msg_id
            )

        except Exception as e:
            print(f"[ERROR] add_message_to_db: {e}")
            return False
    async def add_changed_message_to_db(self, msg: telegram.Message, chat_id: int, user_id: int,msg_id:int, context: ContextTypes.DEFAULT_TYPE):
        text_parser = self.text_parser
        file_func = self.file_func
        content = text_parser.get_message_content_types(msg)
        its_text = content["text"]
        its_photo = content["photo"]
        its_gif = content["gif"]
        its_video = content["video"]
        information = ""
        if its_text:
            information = msg.text or ""
        elif its_photo and msg.photo:
            try:
                photo = msg.photo[-1]  # найбільше фото — останнє
                file_path = await file_func.get_file_func(photo.file_id, context)
                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                information = encoded
            except Exception as e:
                information = f"not backupable information, tags: photo (error)"
                its_photo = 0

        elif its_gif:
            information = "not backupable information, tags: gif"

        elif its_video:
            information = "not backupable information, tags: video"

        else:
            tags = [k for k, v in content.items() if v == 1]
            tag_text = ', '.join(tags) if tags else "none"
            information = f"not backupable information, tags: {tag_text}"
        return init_changed_message_user(
            chat_id=chat_id,
            user_id=user_id,
            information=information,
            its_text=its_text,
            its_photo=its_photo,
            its_gif=its_gif,
            its_video=its_video,
            msg_id=msg_id
        )
class linked_forum_chats:
    def __init__(self):
        self.db = db

    def create_link(self,from_chat_id: int, from_msg_thread_id=0, name:str=""):
        try:
            return self.db.INSERT_Linked_Forum_Chats(from_chat_id, None, from_msg_thread_id,
                                                     None, name)
        except Exception as e:
            print("create_link error:", e)
            return False


    def get_links_by_from_chat(self, from_chat_id: int):
        return self.db.SELECT("Linked_Forum_Chats", "from_chat_id", from_chat_id)

    def get_links_by_to_chat(self, to_chat_id: int):
        return self.db.SELECT("Linked_Forum_Chats", "to_chat_id", to_chat_id)

    def get_links_by_name(self, name: str):
        return self.db.SELECT("Linked_Forum_Chats", "name", name)

    def delete_link_by_id(self, id: int):
        return self.db.DELETE("Linked_Forum_Chats", "id", id)

    def delete_links_by_name(self, name: str):
        return self.db.DELETE("Linked_Forum_Chats", "name", name)


    def update_link_to_chat_and_to_thread_by_name(self, new_to_chat_id, new_to_thread_id, name):
        success = True
        success &= self.db.UPDATE("Linked_Forum_Chats", "to_chat_id", new_to_chat_id, "name", name)
        success &= self.db.UPDATE("Linked_Forum_Chats", "to_msg_thread_id", new_to_thread_id, "name", name)
        return success
    def get_linked(self, from_chat_id, from_message_thread_id):
        results = self.db.SELECT_2WHERE("Linked_Forum_Chats", "from_chat_id", from_chat_id, "from_msg_thread_id", from_message_thread_id)
        if not len(results) == 0:
            return results
        else:
            return False