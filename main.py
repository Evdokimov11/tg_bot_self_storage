from telebot import types
from dotenv import load_dotenv
import telebot
import os
import qrcode
import sqlite3

load_dotenv()
access_token = os.environ['TG_API_KEY']
bot = telebot.TeleBot(access_token)
conn = sqlite3.connect('Self_storage_bd.db', check_same_thread=False)
cursor = conn.cursor()


def create_send_qr(call, name):
    img = qrcode.make('https://docs-python.ru/packages/generator-qr-kodov/')
    type(img)  
    img.save(name)
    img = open(name, 'rb')
    bot.send_photo(call.message.chat.id, img)


def create_event(signal, button, message_to_user):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for name in button:
        markup.add(types.InlineKeyboardButton(name, callback_data= button[name]))
    
    cancel = types.InlineKeyboardButton(text='Отменить', callback_data='fin_cancel')
    markup.add(cancel)
    bot.send_message(signal.message.chat.id, message_to_user,
                     parse_mode='html', reply_markup=markup)


def temporary_function(signal): 
    bot.send_message(signal.message.chat.id, 'message1')


@bot.message_handler(commands=['start'])
def start(message):

    cursor.execute('SELECT telegram_id FROM clients') 
    conn.commit()
    data = cursor.fetchall()
    key = False
    for person in data:
        if message.from_user.id == person[0]: 
            key = True

    if key: 
        bot.send_message(message.chat.id, 'С возвращением в систему')
      
    else:
        bot.send_message(message.chat.id, 
                         'Продолжая использовать приложение вы принимаете пользовательское соглашение')
        cursor.execute('INSERT INTO clients (telegram_id, name, role, mobile_number) VALUES (?, ?, ?,?)', 
                       (message.from_user.id, message.from_user.first_name, "client",""))
        conn.commit()
      
    message_to_customer = f'<b>{message.from_user.first_name}</b>, Укажите вашу роль'
    markup = types.InlineKeyboardMarkup(row_width=3)
    client_button = types.InlineKeyboardButton('Клиент', callback_data='client')
    customer_button = types.InlineKeyboardButton('Заказчик', callback_data='customer')
  
    markup.add(client_button, customer_button)
    bot.send_message(message.chat.id,
                     message_to_customer,
                     parse_mode='html',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('client'))
def start_client(call):
    bot.send_message(call.message.chat.id, 'Пользуйся нами чтобы быть крутым мы тебе очень нужны сердце сердце помидор <3')
    
    buttons = {
    'Хочу получить вещи' : 'cli_get_staff',
    'Хочу сдать вещи' : 'cli_give_staff',
    'Хочу посмотреть FAQ' : 'cli_look_faq'
  }
    message_to_customer = 'Что вы желаете сделать?'
    create_event(call,buttons, message_to_customer)
    buttons.clear()

@bot.callback_query_handler(func=lambda call: call.data.startswith('cli'))
def client_situation(call):
    buttons = {}
    
    if call.data == 'cli_get_staff':
         
        buttons = {
        'Хочу забрать вещи сам' : 'delivery_get_independently',
        'Хочу забрать вещи с помощью курьера' : 'delivery_get_courirer',
        }
        create_event(call,buttons, 'Хотите забрать вещи самостоятельно или забрать с помощью курьера?')
        buttons.clear()
        
    elif call.data == 'cli_give_staff':
        buttons = {
        'Хочу отвезти вещи сам' : 'delivery_give_independently',
        'Хочу отвезти вещи с помощью курьера' : 'delivery_give_courirer',
        }
        create_event(call, buttons, 'Хотите отвезти вещи самостоятельно или воспользоваться бесплатной доставкой?')
        buttons.clear()
      
    elif call.data == 'cli_look_faq':
        bot.send_message(call.message.chat.id, 'FAQ')


@bot.callback_query_handler(func=lambda call: call.data.startswith('delivery_get'))
def client_delivery(call):

    buttons = {
        'Хочу позже вернуть вещи' : 'result_get_return',
        'Не хочу возвращать вещи' : 'result_get_end',
        }
        
    if call.data == 'delivery_get_independently': 
      temporary_function(call)
           
    elif call.data == 'delivery_get_courirer':
      temporary_function(call)
      
    create_event(call,buttons, 'Хотите после этого вернуть вещи?')
    buttons.clear()


@bot.callback_query_handler(func=lambda call: call.data.startswith('delivery_give'))
def measurement_parameters(call):

    buttons = {
        'Хочу ввести параметры' : 'parameters_give',
        'Хочу чтобы мне помогли измерить' : 'parameters_help',
        }
        
    if call.data == 'delivery_give_independently':     
      temporary_function(call)
               
    elif call.data == 'delivery_give_courirer':
      temporary_function(call)
      
    create_event(call,buttons, 'Вы знаете объем и вес или хотите что мы измерили?')
    buttons.clear()


@bot.callback_query_handler(func=lambda call: call.data.startswith('parameters'))
def order_confirmation(call):

    buttons = {
        'Оформляем заказ' : 'result_give_successfully',
        'Хочу отменить заказ' : 'result_give_unsuccesfully',
    }
        
    if call.data == 'parameters_give':     
      temporary_function(call)
               
    elif call.data == 'parameters_help':
      temporary_function(call)
      
    create_event(call,buttons, 'Вы знаете объем и вес или хотите что мы измерили?')
    buttons.clear()

@bot.callback_query_handler(func=lambda call: call.data.startswith('result'))
def handle_bouquet(call):

  if call.data == 'result_get_return':
      create_send_qr(call, "return_qr.png")
        
  elif call.data == 'result_get_end':
      create_send_qr(call, "end_qr.png")
      
  elif call.data == 'result_give_successfully':
      temporary_function(call)
    
  elif call.data == 'result_give_unsuccesfully':
      temporary_function(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('customer'))
def start_customer(call):
    bot.send_message(call.message.chat.id, 'Здравствуйте, что вы хотите сделать?')
    
    buttons = {
    'Хочу узнать количество заказов' : 'cus_orders_number',
    'Хочу выполнить заказ' : 'cus_get_order',
    'Хочу увидеть просроченные заказы' : 'cus_overdue_orders',
    'Хочу посмотреть список клиентов' : 'cus_clients'
    }
  
    message_to_customer = 'Что вы желаете сделать?'
    create_event(call,buttons, message_to_customer)
    buttons.clear()

@bot.callback_query_handler(func=lambda call: call.data.startswith('cus'))
def customer_situation(call):
  
    if call.data == 'cus_clients':
        cursor.execute('SELECT name FROM clients')
        conn.commit()
        data = cursor.fetchall()
        for person in data:
           bot.send_message(call.message.chat.id, person)
      
    elif call.data == 'cus_get_order':
        temporary_function(call)
      
    elif call.data == 'cus_overdue_orders':
        temporary_function(call)
      
    elif call.data == 'cus_orders_number':
        temporary_function(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('fin'))
def handle_price(call):
  if call.data == 'fin_cancel':
    bot.send_message(
      call.message.chat.id,
      'Если хотите изменить услововия, напишите сообщение "/start".')

if __name__ == "__main__":
  bot.polling(non_stop=True)