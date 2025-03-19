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




    user_dont_muted = "Користувач не в RO"
    user_not_found = "Неможливо знайти користувача!"
    incorrect_command = "Неправильно введена команда!"
