from telegram import Bot, BotCommandScopeChat, User

WHITELIST_PATH = 'data/WHITELIST'
PEDNING_PATH = 'data/PENDING'

def __get_list(filename: str) -> list:
    value = []

    try:
        value = open(filename).read().split('\n')
        while '' in value:
            value.remove('')
    except FileNotFoundError:
        open(filename, 'x')

    return value

def __write_list(filename: str, value: list) -> None:
    with open(filename, 'w') as f:
        for x in value:
            f.write(str(x) + '\n')

def __add_list(filename: str, value) -> None:
    __get_list(filename)

    with open(filename, 'a') as f:
        f.write(str(value) + '\n')


def on_authentication(chat_id) -> None:
    from bot import COMMANDS
    from bot import SUCCESS_TEXT

    with open('data/TELEGRAM', 'r') as f:
        token = f.read()
        bot = Bot(token)
        bot.send_message(chat_id, SUCCESS_TEXT)
        bot.set_my_commands(COMMANDS, scope=BotCommandScopeChat(chat_id))

def inspect_interactive():
    pending = get_pending()
    whitelist = get_whitelist()

    new_whitelist = whitelist

    for user in pending:
        name, chat_id = user.split(':')
        first_name, last_name = name.split('#')

        x = input('Add "' + first_name + ' ' + last_name + '" to whitelist? (y/n): ')

        if x == 'y' or x == 'Y' and is_in_whitelist(x):
            new_whitelist.append(str(chat_id))
            on_authentication(chat_id)

    write_pending([])
    write_whitelist(new_whitelist)

def is_in_pending(chat_id: int) -> bool:
    return str(chat_id) in [x.split(':')[1] for x in get_pending()]

def is_in_whitelist(chat_id: int) -> bool:
    return str(chat_id) in get_whitelist()

def get_pending() -> list:
    return __get_list(PEDNING_PATH)

def write_pending(value: list) -> None:
    __write_list(PEDNING_PATH, value)

def add_pending(user: User, chat_id: int) -> None:
    __add_list(PEDNING_PATH, user.first_name + '#' + user.last_name + ':' + str(chat_id))

def get_whitelist() -> list:
    return __get_list(WHITELIST_PATH)

def write_whitelist(value: list) -> None:
    __write_list(WHITELIST_PATH, value)

def add_whitelist(chat_id: int) -> None:
    __add_list(WHITELIST_PATH, str(chat_id))

def main() -> None:
    inspect_interactive()

if __name__ == '__main__':
    main()
