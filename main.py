# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import payment
import qrcode
import datetime
import telebot
import re
from telebot import types
import telebot_calendar
from telebot_calendar import RUSSIAN_LANGUAGE
from telebot_calendar import CallbackData

import certificate
import config
import db_mysql

bot = telebot.TeleBot(config.TELEBOT_TOKEN)

markdown = """
*bold text*
_italic text_
[text](URL)
"""


@bot.message_handler(commands=['start'])
def start(message):

    if not(db_mysql.is_user_exists(message.from_user.id)):    #Если юзер не существует

        msg_txt = config.txt_greeting_anonim()

        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_russian = types.InlineKeyboardButton(text='Россия', callback_data='russian_btn')
        key_ukraine = types.InlineKeyboardButton(text='Украина', callback_data='ukraine_btn')
        keyboard.add(key_russian, key_ukraine)

        bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")

        question = config.txt_question_country()
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="markdown")

    elif db_mysql.is_data_filled(message.from_user.id):
        r_name = db_mysql.get_russian_name(message.from_user.id)
        r_surname = db_mysql.get_russian_surname(message.from_user.id)
        cur_sub = db_mysql.get_subscription(message.from_user.id)
        msg_txt = config.txt_greeting_user(r_name, r_surname, cur_sub)

        new_buttons_menu = config.create_menu(["Получить сертификат", "Продлить подписку"], True)
        bot.send_message(message.from_user.id, msg_txt, reply_markup=new_buttons_menu, parse_mode="markdown")
    else:
        msg_txt = config.txt_greeting_register()
        new_buttons_menu = config.create_menu(["Изменить мои данные"], False)
        bot.send_message(message.from_user.id, msg_txt, reply_markup=new_buttons_menu, parse_mode="markdown")


@bot.message_handler(content_types=['text'])
def get_data(message):
    if message.text == 'Изменить мои данные':
        get_russian_data(message)
    elif (message.text == 'Продлить подписку') and (db_mysql.is_data_filled(message.from_user.id)):
        continue_subscription(message)
    elif (message.text == '1 день') and (db_mysql.is_data_filled(message.from_user.id)):
        continue_sub_day(message)
    elif (message.text == '7 дней') and (db_mysql.is_data_filled(message.from_user.id)):
        continue_sub_week(message)
    elif (message.text == '30 дней') and (db_mysql.is_data_filled(message.from_user.id)):
        continue_sub_month(message)
    elif (message.text == 'Получить сертификат') and (db_mysql.is_data_filled(message.from_user.id)):
        get_certificate(message)
    else:
        start(message)


def get_russian_data(message):

    r_name = db_mysql.get_russian_name(message.from_user.id)
    r_surname = db_mysql.get_russian_surname(message.from_user.id)
    msg_txt = config.txt_enter_data()
    bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown", reply_markup=types.ReplyKeyboardRemove())
    if (r_name == "None") or (r_surname == "None"):
        msg_txt = config.txt_enter_russian_name()
        bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
        bot.register_next_step_handler(message, get_russian_name)
    else:
        message.text = r_surname
        get_russian_surname(message)


def get_english_data(message):
    e_name = db_mysql.get_english_name(message.from_user.id)
    e_surname = db_mysql.get_english_surname(message.from_user.id)
    if (e_name == "None") or (e_surname == "None"):
        msg_txt = config.txt_enter_english_name()
        bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
        bot.register_next_step_handler(message, get_english_name)
    else:
        message.text = e_surname
        get_english_surname(message)


def get_russian_name(message): #получаем фамилию
    db_mysql.update_user(user_id=message.from_user.id, russian_name=str(message.text).upper())
    msg_txt = config.txt_enter_russian_surname()
    bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
    bot.register_next_step_handler(message, get_russian_surname)


def get_russian_surname(message): #Спрашиваем точны ли данные
    db_mysql.update_user(user_id=message.from_user.id, russian_surname=str(message.text).upper())

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_russian_name')  # кнопка «Да»
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_russian_name')
    keyboard.add(key_yes, key_no)

    question = config.txt_question_russian_name(db_mysql.get_russian_name(message.from_user.id), db_mysql.get_russian_surname(message.from_user.id))
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="markdown")


def get_english_name(message): #получаем фамилию
    db_mysql.update_user(user_id=message.from_user.id, english_name=str(message.text).upper())
    msg_txt = config.txt_enter_english_surname()
    bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
    bot.register_next_step_handler(message, get_english_surname)


def get_english_surname(message): #Спрашиваем точны ли данные
    db_mysql.update_user(user_id=message.from_user.id, english_surname=str(message.text).upper())

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_english_name')  # кнопка «Да»
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_english_name')
    keyboard.add(key_yes, key_no)

    question = config.txt_question_english_name(db_mysql.get_english_name(message.from_user.id), db_mysql.get_english_surname(message.from_user.id))
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="markdown")


def get_sex_data(message):
    keyboard = types.InlineKeyboardMarkup()
    key_male = types.InlineKeyboardButton(text='Мужской', callback_data='male_btn')
    key_female = types.InlineKeyboardButton(text='Женский', callback_data='female_btn')
    keyboard.add(key_male, key_female)
    question = config.txt_enter_sex()
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="markdown")


def get_birthday_data(message):
    question = config.txt_enter_birthday()
    bot.send_message(message.from_user.id, text=question, parse_mode="markdown")
    bot.register_next_step_handler(message, get_birthday)


def get_birthday(message):

    birthday = message.text
    datere = re.compile(".*([0-9]{2})-([0-9]{2})-([0-9]{4}).*")

    if datere.match(birthday) is not None:
        m = datere.match(birthday)
        day = m.groups()[0]
        month = m.groups()[1]
        year = m.groups()[2]

        birthday = year + "/" + month + "/" + day
        try:
            datetime.datetime.strptime(birthday, "%Y/%m/%d")
        except:
            get_birthday_data(message)
        else:
            db_mysql.update_user(user_id=message.from_user.id, birthday=birthday)
            get_passport_data(message)
    else:
        get_birthday_data(message)


def get_passport_data(message):
    if db_mysql.get_nationality(message.from_user.id) == '1':
        question = config.txt_enter_passport()
        bot.send_message(message.from_user.id, text=question, parse_mode="markdown")
        bot.register_next_step_handler(message, get_passport)
    else:
        msg_txt = "Не обязательно"
        message.text = msg_txt
        get_passport(message)


def get_passport(message):
    db_mysql.update_user(user_id=message.from_user.id, passport=str(message.text).upper())

    question = config.txt_question_check_data(db_mysql.get_russian_name(message.from_user.id),
        db_mysql.get_russian_surname(message.from_user.id),
        db_mysql.get_english_name(message.from_user.id),
        db_mysql.get_english_surname(message.from_user.id),
        db_mysql.get_sex(message.from_user.id),
        db_mysql.get_birthday(message.from_user.id).strftime("%d-%m-%Y"),
        db_mysql.get_passport(message.from_user.id))

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да, все верно', callback_data='yes_data')
    key_no = types.InlineKeyboardButton(text='Нет, ошибка', callback_data='no_data')
    keyboard.add(key_yes, key_no)

    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard, parse_mode="markdown")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    if call.data == "yes_russian_name":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)  # Убираем клаву ДаНет
        msg_txt = config.txt_thx1()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id
        get_english_data(call.message)

    elif call.data == "no_russian_name":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        db_mysql.update_user(user_id=call.from_user.id, russian_name="None", russian_surname="None")  # Меняем имя юзера в БД
        msg_txt = config.txt_repeat()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id
        get_russian_data(call.message) # Повторяем ввод

    elif call.data == "yes_english_name":
        #db_mysql.update_user(user_id=call.from_user.id, english_name=english_name, english_surname=english_surname) #Меняем имя юзера в БД
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None) # Убираем клаву ДаНет
        msg_txt = config.txt_thx2()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id
        get_sex_data(call.message)

    elif call.data == "no_english_name":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        db_mysql.update_user(user_id=call.from_user.id, english_name="None", english_surname="None")  # Меняем имя юзера в БД
        msg_txt = config.txt_repeat()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id
        get_english_data(call.message)

    elif call.data == "male_btn":
        db_mysql.update_user(user_id=call.from_user.id, user_sex=1)
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        msg_txt = config.txt_male()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id

        get_birthday_data(call.message)

    elif call.data == "female_btn":
        db_mysql.update_user(user_id=call.from_user.id, user_sex=2)
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        msg_txt = config.txt_female()
        bot.send_message(call.from_user.id, text=msg_txt, parse_mode="markdown")
        call.message.from_user.id = call.from_user.id

        get_birthday_data(call.message)

    #Новый юзер, формируем подписку и код
    elif call.data == "yes_data":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        cur_sub = db_mysql.get_subscription(call.from_user.id)

        call.message.from_user.id = call.from_user.id
        generate_qr_code(call.message)
        start(call.message)

    elif call.data == "no_data":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.from_user.id = call.from_user.id

        get_russian_data(call.message) # Повторяем ввод

    elif call.data == "russian_btn":
        db_mysql.insert_user(user_id=call.from_user.id)  # Добавляем юзера в БД
        db_mysql.update_user(user_id=call.from_user.id, user_nationality="1")
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.from_user.id = call.from_user.id

        start(call.message)

    elif call.data == "ukraine_btn":
        db_mysql.insert_user(user_id=call.from_user.id)  # Добавляем юзера в БД
        db_mysql.update_user(user_id=call.from_user.id, user_nationality="2")
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.from_user.id = call.from_user.id

        start(call.message)

    elif call.data == "today_btn":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.text = datetime.datetime.now().strftime("%d-%m-%Y")
        call.message.from_user.id = call.from_user.id
        get_certificate_date(call.message)
    elif call.data == "yesterday_btn":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.text = (datetime.datetime.now()-datetime.timedelta(1)).strftime("%d-%m-%Y")
        call.message.from_user.id = call.from_user.id
        get_certificate_date(call.message)
    elif call.data == "custom_date_btn":
        bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.id, reply_markup=None)
        call.message.from_user.id = call.from_user.id
        bot.register_next_step_handler(call.message, get_certificate_date)
        msg_txt = config.txt_question_cert_date()
        bot.send_message(call.from_user.id, msg_txt, parse_mode="markdown")

def continue_subscription(message):
    msg_txt = config.txt_continue_subscription()
    new_buttons_menu = config.create_menu(["1 день", "7 дней", "30 дней", "Назад"], False)
    bot.send_message(message.from_user.id, msg_txt, reply_markup=new_buttons_menu, parse_mode="markdown")


def continue_sub_day(message):
    db_mysql.update_subscription(message.from_user.id, 1)
    start(message)


def continue_sub_week(message):
    db_mysql.update_subscription(message.from_user.id, 7)
    start(message)


def continue_sub_month(message):
    db_mysql.update_subscription(message.from_user.id, 30)
    start(message)


def get_certificate(message):

    cur_sub = db_mysql.get_subscription(message.from_user.id) - datetime.datetime.now()
    if cur_sub.days >= 0:

        keyboard = types.InlineKeyboardMarkup()
        key_today = types.InlineKeyboardButton(text='Сегодня', callback_data='today_btn')
        key_yesterday = types.InlineKeyboardButton(text='Вчера', callback_data='yesterday_btn')
        key_custom = types.InlineKeyboardButton(text='Другая дата', callback_data='custom_date_btn')
        keyboard.add(key_today, key_yesterday, key_custom)

        msg_txt = config.txt_cert_date_choose()
        bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown", reply_markup=keyboard)

    else:
        msg_txt = config.txt_subscription_finished()
        bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
        start(message)


def get_certificate_date(message):
    cert_date = message.text
    datere = re.compile(".*([0-9]{2})-([0-9]{2})-([0-9]{4}).*")

    if datere.match(cert_date) is not None:
        m = datere.match(cert_date)
        day = m.groups()[0]
        month = m.groups()[1]
        year = m.groups()[2]

        cert_date = year + "/" + month + "/" + day
        try:
            datetime.datetime.strptime(cert_date, "%Y/%m/%d")
        except:
            get_certificate(message)
        else:
            db_mysql.update_user(user_id=message.from_user.id, cert_date=cert_date)
            msg_txt = config.txt_wait()
            bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
            generate_qr_code(message)
            certificate.generate(message)
            filename_pdf = R'.\certificates' + "\\" + str(message.from_user.id) + ".pdf"
            f = open(filename_pdf, "rb")
            bot.send_document(message.chat.id, f)
            msg_txt = "*Ура! Сертификат выдан.*"
            bot.send_message(message.from_user.id, msg_txt, parse_mode="markdown")
            #get_passport_data(message)
    else:
        get_certificate(message)


def generate_qr_code(message):
    # пример данных
    data = "https://www.google.com/search?q="+str(message.from_user.id)
    # имя конечного файла
    filename = '.\\images\\'+str(message.from_user.id)+".png"
    # генерируем qr-код
    img = qrcode.make(data)
    # сохраняем img в файл
    img.save(filename)


bot.polling(none_stop=True, interval=0)
