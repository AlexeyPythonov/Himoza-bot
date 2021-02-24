import telebot
import psycopg2
import os

URL_BRAWL = 'https://www.avito.ru/rossiya?q=%D0%B0%D0%BA%D0%BA%D0%B0%D1%83%D0%BD%D1%82+%D0%B1%D1%80%D0%B0%D0%B2%D0%BB'
URL_SHONG = 'https://www.avito.ru/rossiya?q=%D1%81%D1%82%D1%80%D0%B8%D0%BD%D0%B3%D0%B8+%D0%BC%D1%83%D0%B6%D1%81%D0%BA%D0%B8%D0%B5'

ADMIN_CHAT_ID = 1249187194

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

BUTTON_START = 'В начало'
BUTTON_BRAWL = 'Бабл квас'
BUTTON_SHONG = 'Трусы для больших мальчиков'

def create_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
    return keyboard

KEYBOARD_START = create_keyboard()
KEYBOARD_START.row(BUTTON_BRAWL)
KEYBOARD_START.row(BUTTON_SHONG)


