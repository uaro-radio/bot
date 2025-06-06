from datetime import datetime
from zoneinfo import ZoneInfo

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
        db.INSERT_Users(chat_id, user_id)
        if username == '':
            db.UPDATE_2WHERE("Users", "fullname", full_name, "chat_id", chat_id, "user_id", user_id)
        else:
            db.UPDATE_2WHERE("Users", "username", username, "chat_id", chat_id, "user_id", user_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"init_user | {chat_id} {user_id} {username} {full_name} {call_sign}")
        print(e)
        return False
def init_message_user(chat_id: int, user_id: int, information=0, its_text=0, its_photo=0, its_gif=0, its_video=0, deleted=0,msg_id=0):
    try:
        db.INSERT_Messages(chat_id, user_id, str(information), its_text, its_photo, its_gif, its_video, deleted,msg_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"init_message_user | {chat_id} {user_id} info:{information} text:{its_text} photo:{its_photo} deleted:{deleted}")
        print(e)
        return False
def init_linked_forum_chat(id: int, from_chat_id: int, to_chat_id: int,
                           from_msg_thread_id: int = None,
                           to_msg_thread_id: int = None,
                           name: str = ""):
    try:
        db.INSERT_Linked_Forum_Chats(id, from_chat_id, to_chat_id,
                                    from_msg_thread_id, to_msg_thread_id, name)
        return True
    except Exception as e:
        SQLite_Log.error(f"init_linked_forum_chat | {id=} {from_chat_id=} {to_chat_id=} name={name}")
        print(e)
        return False

def init_changed_message_user(chat_id: int, user_id: int, information=0, its_text=0, its_photo=0, its_gif=0, its_video=0,msg_id=0):
    try:
        db.INSERT_Changed_Messages(chat_id, user_id, str(information), its_text, its_photo, its_gif, its_video, msg_id)
        return True
    except Exception as e:
        SQLite_Log.error(
            f"init_changed_message_user | {chat_id=} {user_id=} info:{information} text:{its_text} photo:{its_photo}"
        )
        print(e)
        return False
def init_analytics_user(chat_id: int, user_id: int):
    try:
        db.INSERT_Analytics(chat_id, user_id)
        return True
    except Exception as e:
        SQLite_Log.error(f"init_analytics_user | {chat_id=} {user_id=}")
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
def update_analytics_msg_count(chat_id:int, user_id:int, msg_count=0):
    try:
        db.UPDATE_2WHERE("Analytics", "msg_count", msg_count, "chat_id", chat_id, "user_id", user_id)
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
def get_messages_by_user(chat_id, user_id):
    return db.SELECT_2WHERE("Messages", "chat_id", chat_id, "user_id", user_id)

def get_changed_messages_by_user(chat_id, user_id):
    return db.SELECT_2WHERE("Changed_Messages", "chat_id", chat_id, "user_id", user_id)

def get_all_messages_by_chat(chat_id):
    return db.SELECT("Messages", "chat_id", chat_id)

def get_all_changed_messages_by_chat(chat_id):
    return db.SELECT("Changed_Messages", "chat_id", chat_id)
def update_messages(chat_id, user_id, column, value):
    return db.UPDATE_2WHERE("Messages", column, value, "chat_id", chat_id, "user_id", user_id)
def delete_messages_by_user(chat_id, user_id):
    return db.DELETE_2WHERE("Messages", "chat_id", chat_id, "user_id", user_id)

def delete_changed_messages_by_user(chat_id, user_id):
    return db.DELETE_2WHERE("Changed_Messages", "chat_id", chat_id, "user_id", user_id)

def get_linked_forum_chats_by_from_chat(from_chat_id):
    return db.SELECT("Linked_Forum_Chats", "from_chat_id", from_chat_id)

def update_linked_forum_to_chat(from_chat_id, to_chat_id, from_message_thread_id, to_message_thread_id):
    return db.UPDATE_3WHERE("Linked_Forum_Chats", "to_message_thread_id", to_message_thread_id, "from_chat_id", from_chat_id, "to_chat_id", to_chat_id)

def delete_linked_forum_chats_by_from_chat(from_chat_id, from_msg_thread_id):
    return db.DELETE_2WHERE("Linked_Forum_Chats", "from_chat_id", from_chat_id, "from_msg_thread_id", from_msg_thread_id)

def delete_linked_forum_chats_by_chats(from_chat_id, to_chat_id):
    return db.DELETE_2WHERE("Linked_Forum_Chats", "from_chat_id", from_chat_id, "to_chat_id", to_chat_id)

