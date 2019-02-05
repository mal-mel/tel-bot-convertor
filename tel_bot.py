import telebot
from telebot import types
from collections import defaultdict
from convertor import convert
from config import token
from num_code import get_cbr_currencies, get_currencies_list

bot = telebot.TeleBot(token)

START, NOMINAL, CUR_2, FINAL = range(4)
USER_STATE = defaultdict(lambda: START)
RESULT_DICT = {}
VALUTE_DICT = {}
currencies_list = get_currencies_list()
cbr_currencies = get_cbr_currencies()


def set_amount(amount):
    RESULT_DICT['amount'] = amount


def set_cur_from(cur_from):
    RESULT_DICT['cur_from'] = cur_from


def set_cur_to(cur_to):
    RESULT_DICT['cur_to'] = cur_to


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=c, callback_data=c)
               for c in currencies_list]
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(func=lambda message: get_state(message) == START)
def start_handler(message):
    bot.send_message(message.chat.id, text='Привет, я бот для проверки курса валют')

    print('USER_ID:', message.from_user.id,
          'USER_USERNAME:', message.from_user.username,
          'LANGUAGE_CODE:', message.from_user.language_code)

    keyboard = create_keyboard()

    bot.send_message(message.chat.id, text='Выбери валюту курс которой хочешь узнать', reply_markup=keyboard)

    update_state(message, NOMINAL)


@bot.callback_query_handler(func=lambda query: get_state(query.message) == NOMINAL)
def callback_handler(callback_query):
    message = callback_query.message
    data = callback_query.data

    VALUTE_DICT['cur_from'] = data

    set_cur_from(cbr_currencies[data])

    bot.send_message(message.chat.id, text=f'Количество {data}?')

    update_state(message, CUR_2)


@bot.message_handler(func=lambda message: get_state(message) == CUR_2)
def cur2_handler(message):
    try:
        message.text = float(message.text)
        set_amount(message.text)
        keyboard = create_keyboard()

        bot.send_message(message.chat.id, text='Выбери вторую валюту', reply_markup=keyboard)

        update_state(message, FINAL)
    except ValueError:
        bot.send_message(message.chat.id, text='Введи корректное числовое значение')


@bot.callback_query_handler(func=lambda query: get_state(query.message) == FINAL)
def final_handler(callback_query):
    message = callback_query.message
    data = callback_query.data

    VALUTE_DICT['cur_to'] = data

    set_cur_to(cbr_currencies[data])

    result = convert(int(RESULT_DICT["amount"]), RESULT_DICT["cur_from"], RESULT_DICT["cur_to"])

    bot.send_message(message.chat.id, text=f'{RESULT_DICT["amount"]} {VALUTE_DICT["cur_from"]} в'
                                           f' {VALUTE_DICT["cur_to"]}:\n'
                                           f'{result} {VALUTE_DICT["cur_to"]}')

    bot.send_message(message.chat.id, text='Перевод завершен, для нового перевода отправь мне любое сообщение')

    update_state(message, START)


bot.polling()
