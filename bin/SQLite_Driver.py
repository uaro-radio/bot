import os as os
import sqlite3 as sql
import dotenv as dotenv
dotenv.load_dotenv()



class DataBase:
    def __init__(self):
        self.DataBase_File = os.getenv("DATABASE_FILE")
    def GenerateNewDataBase(self):
        with open(self.DataBase_File, "w"): pass
        with sql.connect(self.DataBase_File) as db:
            try:
                cursor = db.cursor()
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Users (
                                    chat_id INTEGER,
                                    user_id INTEGER,
                                    username TEXT NOT NULL,
                                    full_name TEXT NOT NULL,
                                    call_sign TEXT NOT NULL,
                                    po_member INTEGER, NOT NULL
                                )
                            """)
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Warns (
                                    chat_id INTEGER,
                                    user_id INTEGER,
                                    expiration_time TEXT,
                                    description TEXT NOT NULL
                                )
                            """)
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS Analytics (
                                    chat_id INTEGER,
                                    user_id INTEGER,
                                    join_date TEXT,
                                    warn_count INTEGER
                                )
                            """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Muted (
                        chat_id INTEGER,
                        user_id INTEGER,
                        expiration_time TEXT,
                        description TEXT
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
    def DELETE(self,TABLE:str,WHERE_COLUMN:str,WHERE_ARGUMENT):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"DELETE FROM {TABLE} WHERE {WHERE_COLUMN}=?", (WHERE_ARGUMENT,))
                return a
            except Exception as e:
                print(e)
                return False
    def INSERT_Users(self,chat_id:int, user_id:int, username:str, fullname:str, call_sign:str, po_member:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                db.cursor().execute(f"INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?)", (chat_id, user_id, username, fullname, call_sign, po_member))
                return True
            except Exception as e:
                print(e)
                return False
    def INSERT_Warns(self,chat_id:int, user_id:int, expiration_time:str, description:str):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"INSERT INTO Warns VALUES(?, ?, ?, ?)", (chat_id, user_id, expiration_time, description))
                return a
            except Exception as e:
                print(e)
                return False
    def INSERT_Analytics(self,chat_id:int, user_id:int, join_date:str, warn_count:int):
        with sql.connect(self.DataBase_File) as db:
            try:
                a = db.cursor().execute(f"INSERT INTO Analytics VALUES(?, ?, ?, ?)", (chat_id, user_id, join_date, warn_count))
                return a
            except Exception as e:
                print(e)
                return False