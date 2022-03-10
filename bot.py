import logging
import telegram
import whitelist
from telegram.error import NetworkError, Unauthorized
from time import sleep, time
from notion_queries import stock_update_query

# texts
GREETING_TEXT = 'Доброго дня! Ви не були авторизовані командою бота. Команда розгляне ваш запит на авторизацію і бот надішле Вам повідомлення у випадку успішної авторизації. Дякуємо!'
WARNING_TEXT = 'Ваш аккаунт ще не пройшов аутентифікацію!'
SUCCESS_TEXT = 'Ваш аккаунт успішно пройшов аутентифікацію!'
STOCK_UPDATE_GREETING_TEXT = 'Виконую запит...'
STOCK_UPDATE_SUCCESS_TEXT = 'Запит успішно виконано.'
STOCK_UPDATE_FAILURE_TEXT = 'Запит виконано з помилкою.'
STOCK_UPDATE_TIME_TEXT = 'Витрачено часу (в секундах): '

COMMANDS = [
    ('/stock_update', 'Виконує запит до Notion бази даних з метою оновити колонку "Запас" в таблиці "Асортимент в наявності"')
]


update_id: int = None
bot: telegram.Bot = None
handler: dict = dict()

def start() -> None:
    global update_id
    global bot

    with open('data/TELEGRAM', 'r') as f:
        token = f.read()
        bot = telegram.Bot(token)

        try:
            update_id = bot.get_updates()[0].update_id
        except IndexError:
            update_id = None

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        while True:
            try:
                __process(bot)
            except NetworkError:
                sleep(1)
            except Unauthorized:
                update_id += 1

def __process(bot) -> None:
    global update_id

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            if authenticate(update):
                text = update.message.text

                if text in handler:
                    handler[text](update)

def authenticate(update) -> bool:
    user = update.message.from_user
    chat_id = update.message.chat.id

    if whitelist.is_in_whitelist(chat_id):
        return True
    
    if not whitelist.is_in_pending(chat_id):
        update.message.reply_text(GREETING_TEXT)
        whitelist.add_pending(user, chat_id)
    elif not whitelist.is_in_whitelist(chat_id):
        update.message.reply_text(WARNING_TEXT)

    return False

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
