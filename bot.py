import logging
import telegram
import whitelist
from telegram.error import NetworkError, Unauthorized
from time import sleep, time
from notion_queries import stock_update_query

# texts
GREETING_TEXT = 'Доброго дня! Ви не були авторизовані командою бота. Команда розгляне ваш запит на авторизацію і бот надішле Вам повідомлення у випадку успішної авторизації. Дякуємо!'
AUTH_WARNING_TEXT = 'Ваш аккаунт ще не пройшов аутентифікацію!'
AUTH_SUCCESS_TEXT = 'Ваш аккаунт успішно пройшов аутентифікацію!'
STOCK_UPDATE_GREETING_TEXT = 'Виконую запит...'
STOCK_UPDATE_SUCCESS_TEXT = 'Запит успішно виконано.'
STOCK_UPDATE_FAILURE_TEXT = 'Запит виконано з помилкою.'
STOCK_UPDATE_TIME_TEXT = 'Витрачено часу (в секундах): '

COMMANDS = [
    ('/stock_update', 'Виконує запит до Notion бази даних з метою оновлення колонки "Запас" в таблиці "Асортимент в наявності"')
]


update_id = None
bot: telegram.Bot = None
handler = {}

def start():
    global update_id
    global bot

    with open('tokens/TELEGRAM', 'r') as f:
        token = f.read().replace('\n', '')
        bot = telegram.Bot(token)

        try:
            update_id = bot.get_updates()[0].update_id
        except IndexError:
            update_id = None

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        while True:
            try:
                __process()
            except NetworkError:
                sleep(1)
            except Unauthorized:
                update_id += 1


def __process():
    global update_id
    global bot

    whitelist.notify_authenticated(on_authentication)

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            auth_code = whitelist.authenticate(update)

            if auth_code == whitelist.WHITELIST:
                text = update.message.text

                if text in handler:
                    handler[text](update)
            elif auth_code == whitelist.UNKNOWN:
                update.message.reply_text(GREETING_TEXT)
            elif auth_code == whitelist.PENDING:
                update.message.reply_text(AUTH_WARNING_TEXT)

def on_authentication(chat_id):
    global bot

    bot.send_message(chat_id, AUTH_SUCCESS_TEXT)
    bot.set_my_commands(COMMANDS, scope=telegram.BotCommandScopeChat(chat_id))

def stock_update(update: telegram.Update):
    update.message.reply_text(STOCK_UPDATE_GREETING_TEXT)

    msg = ''
    now = time()
    try:
        stock_update_query()
        msg += STOCK_UPDATE_SUCCESS_TEXT
    except:
        msg += STOCK_UPDATE_FAILURE_TEXT
    elapsed = time() - now
    msg += '\n' + STOCK_UPDATE_TIME_TEXT + str(elapsed)

    update.message.reply_text(msg)

handler[COMMANDS[0][0]] = stock_update
