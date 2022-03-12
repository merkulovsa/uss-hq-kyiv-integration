import telegram
import argparse

UNKNOWN = 0
PENDING = 1
WHITELIST = 2

__WHITELIST_PATH = 'data/WHITELIST_WHITELIST'
__PENDING_PATH = 'data/WHITELIST_PENDING'
__NOTIFY_PATH = 'data/WHITELIST_NOTIFY'

def __get_list(filename: str) -> list:
    value = []

    try:
        value = open(filename).read().split('\n')
        while '' in value:
            value.remove('')
    except FileNotFoundError:
        open(filename, 'x')

    return value

def __write_list(filename: str, value: list):
    with open(filename, 'w') as f:
        for x in value:
            f.write(str(x) + '\n')

def __add_list(filename: str, value):
    __get_list(filename)

    with open(filename, 'a') as f:
        f.write(str(value) + '\n')


def is_in_pending(chat_id: int) -> bool:
    return str(chat_id) in [x.split(':')[1] for x in __get_list(__PENDING_PATH)]

def is_in_whitelist(chat_id: int) -> bool:
    return str(chat_id) in __get_list(__WHITELIST_PATH)

def authenticate(update: telegram.Update) -> int:
    user = update.message.from_user
    chat_id = update.message.chat.id

    if is_in_whitelist(chat_id):
        return WHITELIST

    if not is_in_pending(chat_id):
        __add_list(__PENDING_PATH, str(user.first_name) + '#' + str(user.last_name) + ':' + str(chat_id))
        return UNKNOWN
    elif not is_in_whitelist(chat_id):
        return PENDING

def inspect():
    global __on_authentication

    pending = __get_list(__PENDING_PATH)
    whitelist = __get_list(__WHITELIST_PATH)
    notify = __get_list(__NOTIFY_PATH)

    new_pending = []
    new_whitelist = whitelist
    new_notify = notify

    if len(pending) == 0:
        print('There are no values in pending list.')
        return

    for user in pending:
        name, chat_id = user.split(':')
        first_name, last_name = name.split('#')

        x = input('Add "' + first_name + ' ' + last_name + '" to whitelist? (y/n): ')

        if x == 'y' or x == 'Y':
            new_whitelist.append(chat_id)
            new_notify.append(chat_id)
        elif x == 'n' or x == 'N':
            pass
        else:
            new_pending.append(user)

    __write_list(__WHITELIST_PATH, new_whitelist)
    __write_list(__PENDING_PATH, new_pending)
    __write_list(__NOTIFY_PATH, new_notify)

def clear():
    __write_list(__WHITELIST_PATH, [])
    __write_list(__PENDING_PATH, [])
    __write_list(__NOTIFY_PATH, [])

def notify_authenticated(callback):
    notifiers = __get_list(__NOTIFY_PATH)

    for chat_id in notifiers:
        callback(chat_id)

    __write_list(__NOTIFY_PATH, [])

def main():
    parser = argparse.ArgumentParser('whitelist tool for telegram bot')
    parser.add_argument('-i', '--inspect', dest='inspect', action='store_true', help='run pending list inspection')
    parser.add_argument('-c', '--clear', dest='clear', action='store_true', help='clear pending and whitelist lists')
    
    args = parser.parse_args()

    if args.inspect:
        inspect()
    elif args.clear:
        clear()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
