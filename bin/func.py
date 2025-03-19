import os
import re
import ssl
import sys

from bin.Logging import SQLite_Log, Core_Log
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