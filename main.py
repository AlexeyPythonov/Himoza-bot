from settings.settings import *
from parse.Parse import Parse
from parse.dataParse import Data
from himoza_keys import PUBL, SECR, TOKEN

import psycopg2
import telebot

import requests
import json
from datetime import datetime as dt
from datetime import date
import pytz
import uuid

bot = telebot.TeleBot(TOKEN)

keyboard_choice = create_keyboard()
keyboard_choice.row(BUTTON_START)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Какой раздел вас интересует?', reply_markup=KEYBOARD_START)

@bot.message_handler(commands=['himoza'])
def buy_smile(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    times_1 = telebot.types.InlineKeyboardButton('1 раз', callback_data='1t')
    times_2 = telebot.types.InlineKeyboardButton('2 раза', callback_data='2t')
    times_5 = telebot.types.InlineKeyboardButton('5 раз', callback_data='5t')
    times_10 = telebot.types.InlineKeyboardButton('10 раза', callback_data='10t')
    times_100 = telebot.types.InlineKeyboardButton('100 раз', callback_data='100t')
    start = telebot.types.InlineKeyboardButton('в начало((', callback_data='st')
    markup.add(times_1, times_2, times_5, times_10, times_100, start)

    bot.send_message(message.chat.id, 'Сколько раз хотите порадовать разработчика?\n1руб = 1 раз)', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def smile(call):
    if call.message:
        if call.data == 'st':
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'Вы вышли в главное меню')
            start_message(call.message)
        elif call.data == 'check_pay':
            user = int(call.message.chat.id)
            cur = conn.cursor()
            cur.execute('SELECT urlbill FROM users WHERE user_id = %s', (user,))
            
            for i in cur.fetchone():
                bill = i

            cur.close()
            

            get_info_bill = requests.get(f'https://api.qiwi.com/partner/bill/v1/bills/{bill}',
                headers={'Authorization': f'Bearer {SECR}',
                        'Accept': 'application/json'
                }
            )

            info_bill = get_info_bill.json()

            if info_bill['status']['value'] == 'PAID':
                markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                again = telebot.types.InlineKeyboardButton('ОБРАДОВАТЬ ЕЩЕ РАЗ😼', callback_data='again')
                markup.add(again)
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '😼РАЗРАБ СИЯЕТ ОТ СЧАСТЬЯ🍆', reply_markup=markup)
            else:
                bot.answer_callback_query(callback_query_id=call.id, text="🖕ПЛАТЕЖ НЕ НАЙДЕН🖕", show_alert=True)
        
        elif call.data == 'again':
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'ОБРАДУЙ РАЗРАБА🍆')
            buy_smile(call.message)
                
        else:
            summ = 0.00
            comm = ''
            if call.data == '1t':
                summ = 1.00
                comm = '1 раз порадовать'

            elif call.data == '2t':
                summ = 2.00
                comm = '2 раза порадовать'

            elif call.data == '5t':
                summ = 5.00
                comm = '5 раз порадовать'

            elif call.data == '10t':
                summ = 10.00
                comm = '10 раз порадовать'

            elif call.data == '100t':
                summ = 100.00
                comm = '100 раз порадовать'

            

            payUrl, bill = paySmile(summ, comm)

            user = int(call.message.chat.id)

            bill = str(bill)
            
            cur = conn.cursor()

            cur.execute('SELECT id FROM users WHERE user_id = %s', (user,))
            if cur.fetchall() == []:

                cur.execute('INSERT INTO users(user_id, urlbill) VALUES(%s, %s)', (user, bill,))
                conn.commit()
                
            
            else:
                cur.execute('UPDATE users SET urlbill = %s WHERE user_id = %s', (bill, user,))
                conn.commit()
                
            cur.close()

            markup = telebot.types.InlineKeyboardMarkup()
            payButton = telebot.types.InlineKeyboardButton(text='Оплатить', url=payUrl)
            CheckPay = telebot.types.InlineKeyboardButton('Проверить оплату', callback_data='check_pay')               
            markup.add(payButton, CheckPay)

            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '✅ Счёт на оплату сформирован. 😼После оплаты разраб обрадуется!😼(для оплаты используйте последнюю отправленную вам ссылку)', reply_markup= markup)

def paySmile(summ, comm):
    headers={'Authorization': f'Bearer {SECR}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }

    local_date = dt.now(pytz.timezone('Asia/Vladivostok'))
    current_time = str(local_date.time())
    time = current_time.rpartition('.')[0]
    day = local_date.date()
    exp_date = f'{day}T{time}+03:00'
    print(exp_date)
    
    params={'amount': {'value': summ, 
                        'currency': 'RUB',
                    },
                'comment': comm, 
                'expirationDateTime': exp_date,
                'customer': {}, 
                'customFields': {},        
            }
    
    params = json.dumps(params)
    
    

    loop = True
    
    while loop:  
        cur = conn.cursor()   
        bill = uuid.uuid4()
        bill = str(bill)
        cur.execute('SELECT id FROM users WHERE urlbill = %s', (bill,))  
        if cur.fetchall() == []:
            loop = False
        
        cur.close()
  
    cur.close()
    
    
    bills = f'https://api.qiwi.com/partner/bill/v1/bills/{bill}'
    
    

    g = requests.put(bills,
        headers=headers,
        data=params,
    )
    
    
    g.json()
    
    
    

    get_info_bill = requests.get(bills,
        headers={'Authorization': f'Bearer {SECR}',
                'Accept': 'application/json'
        }
    )
    info_bill = get_info_bill.json()
    
    
    
    payUrl = info_bill['payUrl']

    return payUrl, bill
    
    
@bot.message_handler(commands=['admin_panel'])
def admin_panel(message):
    if ADMIN_CHAT_ID == message.chat.id:
        bot.send_message(message.chat.id, "Привет, повелитель")
    else:
        bot.send_message(message.chat.id, "Вам недоступна админская панель, напишите /start")

@bot.message_handler(commands=['vk_author'])
def vk_author(message):
    markup = telebot.types.InlineKeyboardMarkup()
    BTN_MY_VK= telebot.types.InlineKeyboardButton(text='ВК автора', url='https://vk.com/pit0nov')
    VK_AUTHORS = markup.add(BTN_MY_VK)
    bot.send_message(message.chat.id, "Тыкни и поставь луйк на аву автора", reply_markup = VK_AUTHORS)

@bot.message_handler(content_types=['text'])
def get_messages(message):

    global site, values

    if message.text == BUTTON_BRAWL:
        site = Parse(URL_BRAWL).get_content()
        values = Data(site)

        i = 0    
        while i < len(values.names):
            bot.send_photo(message.chat.id, photo=values.img[i], caption=f'название: {values.names[i]} \nцена: {values.price[i]} \nразмещено: {values.date[i]}')
            i += 1     
    
    elif message.text == BUTTON_SHONG:
        site = Parse(URL_SHONG).get_content()
        values = Data(site)

        i = 0
        while i < len(values.names):
            bot.send_photo(message.chat.id, photo=values.img[i], caption=f'название: {values.names[i]} \nцена: {values.price[i]} \nразмещено: {values.date[i]}')
            i += 1
    
    elif message.text == BUTTON_START:
        start_message(message)

    else:
        bot.send_photo(message.chat.id, photo='http://risovach.ru/upload/2014/05/mem/chelovechek_50565355_orig_.jpeg', caption='Я тебя не понял, я же бот(\nнажми /start')

    bot.send_chat_action(message.chat.id, 'typing')

bot.polling()
