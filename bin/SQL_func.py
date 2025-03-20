import bin.SQLite_Driver as sql_drv
from bin.Logging import SQLite_Log
db = sql_drv.DataBase()

def is_user_exist(chat_id:int, user_id:int):
    results = db.SELECT_2WHERE("Users", "chat_id", chat_id, "user_id", user_id)
    if results == False:
        SQLite_Log.error(f"is_user_exist | {chat_id} {user_id}")
    return True if len(results) > 0 else False
def init_user(chat_id: int, user_id: int, username="", full_name="", call_sign="", po_member=0):
    try:
        db.INSERT_Users(chat_id, user_id, username, full_name, call_sign, po_member)
        return True
    except Exception as e:
        SQLite_Log.error(f"init_user | {chat_id} {user_id} {username} {full_name} {call_sign}")
        print(e)
        return False
def update_user_username(chat_id:int, user_id:int, username:str):
    try:
        db.UPDATE_2WHERE("Users", "username", username, "chat_id", chat_id, "user_id", user_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"update_user_username | {chat_id} {user_id}")
        print(e)
        return False
def update_user_callsign(chat_id:int, user_id:int, call_sign:str):
    try:
        db.UPDATE_2WHERE("Users", "call_sign", call_sign, "chat_id", chat_id, "user_id", user_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"update_user_callsign | {chat_id} {user_id}")
        print(e)
        return False
def update_user_fullname(chat_id:int, user_id:int, fullname:str):
    try:
        db.UPDATE_2WHERE("Users", "full_name", fullname, "chat_id", chat_id, "user_id", user_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"update_user_fullname | {chat_id} {user_id}")
        print(e)
        return False
def get_user(chat_id, user_id):
    user = db.SELECT_2WHERE("Users", "chat_id", chat_id, "user_id", user_id)
    return user[0] if len(user) > 0 else False
def get_user_by_username(chat_id, username):
    user = db.SELECT_2WHERE("Users", "chat_id", chat_id, "username", username)
    return user[0] if len(user) > 0 else False
def get_user_warns(chat_id, user_id):
    user = db.SELECT_2WHERE("Warns", "chat_id", chat_id, "user_id", user_id)
    return user[0] if len(user) > 0 else False
def get_user_analytics(chat_id, user_id):
    user = db.SELECT_2WHERE("Analytics", "chat_id", chat_id, "user_id", user_id)
    return user[0] if len(user) > 0 else False