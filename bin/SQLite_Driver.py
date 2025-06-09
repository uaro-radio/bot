import os as os
import random
import sqlite3 as sql
from datetime import datetime
from zoneinfo import ZoneInfo

import dotenv as dotenv
dotenv.load_dotenv()



class DataBase:
    def __init__(self):
        self.DataBase_File = os.getenv("DATABASE_FILE")
    def GenerateNewDataBase(self):
        with sql.connect(self.DataBase_File) as db:
            try:
                cursor = db.cursor()
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Users (
                                    chat_id INTEGER NOT NULL,
                                    user_id INTEGER NOT NULL,
                                    username TEXT,
                                    full_name TEXT,
                                    call_sign TEXT,
                                    po_member INTEGER,
                                    verificated INTEGER
                                )
                            """)
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Warns (
                                    chat_id INTEGER NOT NULL,
                                    user_id INTEGER NOT NULL,
                                    expiration_time TEXT,
                                    description TEXT 
                                )
                            """)
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Analytics (
                                    chat_id INTEGER NOT NULL,
                                    user_id INTEGER NOT NULL,
                                    join_date TEXT,
                                    warn_count INTEGER,
                                    thx_count INTEGER,
                                    msg_count INTEGER
                                )
                            """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Restricted (
                        chat_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        ban_all_media INTEGER,
                        ban_gif INTEGER,
                        ban_stickers INTEGER
                        );
                """)
                cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Messages (
                            chat_id INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            information INTEGER,
                            its_text INTEGER,
                            its_photo INTEGER,
                            its_gif INTEGER,
                            its_video INTEGER,
                            created_at TEXT,
                            deleted INTEGER,
                            msg_id INTEGER
                            );
                                """)
                cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Changed_Messages (
                            chat_id INTEGER NOT NULL,
                            user_id INTEGER NOT NULL,
                            information INTEGER,
                            its_text INTEGER,
                            its_photo INTEGER,
                            its_gif INTEGER,
                            its_video INTEGER,
                            when_changed TEXT,
                            msg_id INTEGER
                            );
                                                """)
                cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Linked_Forum_Chats (
                            id INTEGER,
                            from_chat_id INTEGER NOT NULL,
                            to_chat_id INTEGER,
                            from_msg_thread_id INTEGER NOT NULL,
                            to_msg_thread_id INTEGER,
                            name TEXT NOT NULL
                            );
                                                                """)
            except Exception as e:
                print(e)
                return False
    def sendDirectSQL(self,query: str):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(query).fetchall()
                return a
            except Exception as e:
                print(e)
                return False
    def SELECT(self,TABLE:str, WHERE_COLUMN:str, WHERE):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"SELECT * FROM {TABLE} WHERE {WHERE_COLUMN}=?", (WHERE,)).fetchall()
                return a
            except Exception as e:
                print(e)
                return False
    def SELECT_2WHERE(self,TABLE:str, WHERE_COLUMN:str, WHERE, WHERE_COLUMN2:str, WHERE2):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"SELECT * FROM {TABLE} WHERE {WHERE_COLUMN}=? AND {WHERE_COLUMN2}=?", (WHERE, WHERE2)).fetchall()
                return a
            except Exception as e:
                print(e)
                return False
    def UPDATE(self,TABLE:str,COLUMN:str,ARGUMENT,WHERE_COLUMN:str, WHERE_ARGUMENT):
        with sql.connect(self.DataBase_File) as db:
            try:
                db.cursor().execute(f"UPDATE {TABLE} SET {COLUMN}=? WHERE {WHERE_COLUMN}=?", (ARGUMENT,WHERE_ARGUMENT))
                return True
            except Exception as e:
                print(e)
                return False
    def UPDATE_2WHERE(self,TABLE:str,COLUMN:str,ARGUMENT,WHERE_COLUMN:str, WHERE_ARGUMENT, WHERE_COLUMN2:str, WHERE_ARGUMENT2):
        with sql.connect(self.DataBase_File) as db:
            try:
                db.cursor().execute(f"UPDATE {TABLE} SET {COLUMN}=? WHERE {WHERE_COLUMN}=? AND {WHERE_COLUMN2}=?", (ARGUMENT,WHERE_ARGUMENT,WHERE_ARGUMENT2))
                return True
            except Exception as e:
                print(e)
                return False

    def UPDATE_3WHERE(self, TABLE: str, COLUMN: str, ARGUMENT,WHERE_COLUMN1: str, WHERE_ARGUMENT1,WHERE_COLUMN2: str, WHERE_ARGUMENT2,WHERE_COLUMN3: str, WHERE_ARGUMENT3):
        with sql.connect(self.DataBase_File) as db:
            try:
                db.cursor().execute(
                    f"""UPDATE {TABLE} 
                        SET {COLUMN}=?
                        WHERE {WHERE_COLUMN1}=? AND {WHERE_COLUMN2}=? AND {WHERE_COLUMN3}=?""",
                    (ARGUMENT, WHERE_ARGUMENT1, WHERE_ARGUMENT2, WHERE_ARGUMENT3)
                )
                return True
            except Exception as e:
                print(e)
                return False

    def DELETE(self,TABLE:str,WHERE_COLUMN:str,WHERE_ARGUMENT):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"DELETE FROM {TABLE} WHERE {WHERE_COLUMN}=?", (WHERE_ARGUMENT,))
                return a
            except Exception as e:
                print(e)
                return False

    def DELETE_2WHERE(self, TABLE: str, WHERE_COLUMN: str, WHERE_ARGUMENT, WHERE_COLUMN2: str, WHERE_ARGUMENT2):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(
                    f"DELETE FROM {TABLE} WHERE {WHERE_COLUMN}=? AND {WHERE_COLUMN2}=?",
                    (WHERE_ARGUMENT, WHERE_ARGUMENT2)
                )
                return a
            except Exception as e:
                print(e)
                return False

    def INSERT_Users(self,chat_id:int, user_id:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                db.cursor().execute(f"INSERT INTO Users(chat_id, user_id) VALUES(?, ?)", (chat_id, user_id))
                return True
            except Exception as e:
                print(e)
                return False
    def INSERT_Restricted(self,chat_id:int, user_id:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"INSERT INTO Restricted(chat_id, user_id) VALUES(?, ?)", (chat_id, user_id))
                return a
            except Exception as e:
                print(e)
                return False
    def INSERT_Messages(self, chat_id, user_id, information=0, its_text=0, its_photo=0, its_gif=0, its_video=0,
                        deleted=0,msg_id=0):
        created_at = datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()
        try:
            with sql.connect(self.DataBase_File) as db:
                db.execute("""
                    INSERT INTO Messages (
                        chat_id, user_id, information, its_text, its_photo, its_gif, its_video, created_at, deleted, msg_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                """, (chat_id, user_id, information, its_text, its_photo, its_gif, its_video, created_at, deleted,msg_id))
                return True
        except Exception as e:
            print("Insert into Messages error:", e)
            return False

    def INSERT_Changed_Messages(self, chat_id, user_id, information=0, its_text=0, its_photo=0, its_gif=0, its_video=0,msg_id=0):
        when_changed = datetime.now(ZoneInfo("Europe/Kyiv")).isoformat()
        try:
            with sql.connect(self.DataBase_File) as db:
                db.execute("""
                    INSERT INTO Changed_Messages (
                        chat_id, user_id, information, its_text, its_photo, its_gif, its_video, when_changed,msg_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
                """, (chat_id, user_id, information, its_text, its_photo, its_gif, its_video, when_changed,msg_id))
                return True
        except Exception as e:
            print("Insert into Changed_Messages error:", e)
            return False
    def INSERT_Analytics(self,chat_id:int, user_id:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"INSERT INTO Analytics(chat_id, user_id, msg_count) VALUES(?, ?,'1')", (chat_id, user_id))
                return a
            except Exception as e:
                print(e)
                return False
    def INSERT_Warns(self,chat_id:int, user_id:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"INSERT INTO Warns(chat_id, user_id) VALUES(?, ?)", (chat_id, user_id))
                return a
            except Exception as e:
                print(e)
                return False

    def INSERT_Linked_Forum_Chats(self,from_chat_id, to_chat_id, from_msg_thread_id=None, to_msg_thread_id=None,
                                 name=""):
        id = random.randint(0, 9999999999)

        try:
            with sql.connect(self.DataBase_File) as db:
                db.execute("""
                    INSERT INTO Linked_Forum_Chats (id,
                        from_chat_id, to_chat_id, from_msg_thread_id, to_msg_thread_id, name
                    ) VALUES (?, ?, ?, ?, ?,?)
                """, (id,from_chat_id, to_chat_id, from_msg_thread_id, to_msg_thread_id, name))
            return True
        except Exception as e:
            print("Insert into Linked_Forum_Chats error:", e)
            return False
