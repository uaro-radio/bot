from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class Inline_Keyboard:
    cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Скасувати", callback_data="sell-cancel")]])

    def SS_to_admin(self, user_id):
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Одобрити", callback_data=f"sell-accept_{user_id}"),
                                      InlineKeyboardButton("❌ Відхилити", callback_data=f"sell-deny_{user_id}")]])
