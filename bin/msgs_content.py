class MessagesText:
    def placeholders_to_information(self,msg:str, placeholders_and_infromation:list) -> str:
        for x in placeholders_and_infromation:
            msg=msg.replace(str(x[0]), str(x[1]))
        return msg

    mute_command_message = ('Користувач $USER$ переведений в режим RO(Read Only)\n'
                            #'\u2022 <b>Причина:</b> $REASON$\n'
                            '\u2023 <b>До</b>: $EXP_DATE$\n'
                            '\u2022 <i><b>Адміністратор</b></i>: $ADMIN_NAME$')
    unmute_command_message = ('Користувач $USER$ виведений з RO\n'
                            '\u2022 <i><b>Адміністратор</b></i>: $ADMIN_NAME$')

    profile_message = ("📌 <b>Профіль користувача $USER$</b>\n\n"
                       "❤️ Репутація: <i>$REP$</i>")

    start_message = ("Це офіційний бот чату UARO: Ukrainian Аmateur Radio Operators\n"
                     '<a href="https://t.me/Ukraine_Amateur_Radio_Operators">Натисни сюди для вступу</a>\n'
                     '<a href="https://telegra.ph/Bot-UARO-komandi-ta-%D1%96nformac%D1%96ya-06-07">Команди, інформація</a>')
    user_dont_muted = "Користувач не в RO"
    user_not_found = "Неможливо знайти користувача!"
    incorrect_command = "Неправильно введена команда!"
