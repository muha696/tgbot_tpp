import telebot
from telebot import TeleBot, types
import config
from dbwork import DBbot
from random_code import random_tutor_code
import emoji

def check_admin(user_name):
    if user_name == 'admin_name':
        result = True
    else:
        result = False
    return result


bot = telebot.TeleBot(config.TOKEN)
db = DBbot('db_shed.db')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Данный бот предназначен для аттестации студентов по дисциплинам \n /regstudent - Регистрация студента \n '
                                      '/study - Просмотр дисциплин')
    bot.send_message(message.chat.id,
                     'Для преподавателей \n /add_disp - Добавление дисциплины \n '
                     '/disp_list - Просмотр дисциплин')


@bot.message_handler(commands=['add_tutor'])

def register(message):
    if check_admin(message.from_user.username):
        mesg = bot.send_message(message.chat.id, 'Повелитель, введите ФИО преподавателя (полное)')
        bot.register_next_step_handler(mesg, add_tutor)

def add_tutor(message):
    tutor_db = message.text.split()
    check_code = random_tutor_code()
    surname = tutor_db[0]
    name = tutor_db[1]
    patronomic = tutor_db[2]
    db.reg_tutor_admin(surname, name, patronomic, check_code)
    bot.send_message(message.chat.id, f"Преподаватель {surname} {name} {patronomic} зарегистрирован! Код потверждения `{check_code}`", parse_mode="MARKDOWN")


@bot.message_handler(commands=['regtutor'])
def code_input(message):
    if not db.check_tutor(message.from_user.id):
        mesg = bot.send_message(message.chat.id, 'Введите ключ')
        bot.register_next_step_handler(mesg, add_tutor_tgid)
    else:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')

def add_tutor_tgid(message):
    if db.check_code(message.text):
        db.reg_tutor_end(message.text, message.from_user.id, message.chat.id)
        db.add_user(message.from_user.id)
        bot.send_message(message.chat.id, 'Вы успешно зарегистрированы!')
    else:
        bot.send_message(message.chat.id, 'Такого ключа нет')


@bot.message_handler(commands=['regstudent'])

def register(message):
    if not db.user_check(message.from_user.id):
        mesg = bot.send_message(message.chat.id, 'Введите следующие данные: Фамилия и номер группы')
        bot.register_next_step_handler(mesg, add_student)
    else:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')

def add_student(message):
    student_db = message.text.split()
    surname = student_db[0]
    group = int(student_db[1])
    db.register_student(surname, group, message.from_user.id, message.chat.id)
    db.add_user(message.from_user.id)
    bot.send_message(message.chat.id, f"Вы успешно зарегистрированы!")

@bot.message_handler(commands=['add_disp'])
def start_add(message):
    if db.check_tutor(message.from_user.id):
        msg = bot.send_message(message.chat.id, 'Регистрация дисциплины в базе данных. Введите название:')
        bot.register_next_step_handler(msg, dsname)
    else:
        bot.send_message(message.chat.id, 'Нет доступа')

def dsname(message):
    ds_nm = message.text
    with db.con:
        db.cur.execute(f"""INSERT INTO disciplines (discipline_name, tutor) VALUES ('{ds_nm}', '{message.from_user.id}')""")
        ds_id = db.cur.execute(f"""SELECT id FROM disciplines WHERE discipline_name = '{ds_nm}'""").fetchone()
    ds_id = ds_id[0]
    msg = bot.send_message(message.chat.id, 'Введите учебную группу:')
    bot.register_next_step_handler(msg, dsgroup, ds_id)

def dsgroup(message, ds_id):
    ds_group = message.text
    with db.con:
        db.cur.execute(f"""UPDATE disciplines SET group_study = '{ds_group}' WHERE id = '{ds_id}'""")
    msg = bot.send_message(message.chat.id, 'Введите аттестацию:')
    bot.register_next_step_handler(msg, dsatt, ds_id)

def dsatt(message, ds_id):
    ds_att = message.text
    with db.con:
        db.cur.execute(f"""UPDATE disciplines SET attestation = '{ds_att}' WHERE id = '{ds_id}'""")
    bot.send_message(message.chat.id, 'Дисциплина добавлена')


@bot.message_handler(commands=['disp_list'])

def my_disp(message):
    if db.check_tutor(message.from_user.id):
        disciplines = db.select_info(data='discipline_name', table='disciplines', column='tutor', value=message.from_user.id)
        disciplines_id = db.select_info(data='id', table='disciplines', column='tutor', value=message.from_user.id)
        disciplines_group = db.select_info(data='group_study', table='disciplines', column='tutor', value=message.from_user.id)
        ds_name = []
        ds_id = []
        ds_gp = []
        for i in disciplines:
            ds_name.append(i[0])
        for i in disciplines_id:
            ds_id.append(i[0])
        for i in disciplines_group:
            ds_gp.append(i[0])


        disciplines_dict = dict(zip(ds_id, ds_name))

        kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        name_to_kb = []
        for i in range(len(ds_name)):
            name_to_kb.append(f'{ds_name[i]}')

        kb_disp = [types.KeyboardButton(text=x) for x in name_to_kb]
        kb.add(*kb_disp)
        msg = bot.send_message(message.chat.id,
                                   f'Ваши дисциплины загружены! Выберите дисциплину',
                                   reply_markup=kb)

        bot.register_next_step_handler(msg, status_look, disciplines_dict)

def status_look(message, disciplines_dict):

    for k, v in disciplines_dict.items():
        if v == message.text:
            ds_id = k

    with db.con:
        student_to_check = db.cur.execute(f"""SELECT * FROM check_att WHERE discipline_id = '{ds_id}'""").fetchall()
        student_to_check_ds = db.cur.description
    student_to_check_dict = [dict(zip([col[0] for col in student_to_check_ds], row)) for row in student_to_check]
    if bool(student_to_check_dict) == True:
        for i in student_to_check_dict:
            student_id = i['student_id']
            with db.con:
                select_student = db.cur.execute(f"""SELECT * FROM students WHERE user_id = '{student_id}' """).fetchall()
                select_student_ds = db.cur.description
        select_student_to_dict = [dict(zip([col[0] for col in select_student_ds], row)) for row in select_student]
        for i in student_to_check_dict:
            for j in select_student_to_dict:
                if i['student_id'] == j['user_id']:
                    kb = types.InlineKeyboardMarkup(row_width=4)
                    kb_check = types.InlineKeyboardButton(text='Принять на проверку',
                                                callback_data='on_check' + str(i['id']))
                    kb_def = types.InlineKeyboardButton(text=f"К защите",
                                                callback_data='admwork' + str(i['id']))
                    kb_adm = types.InlineKeyboardButton(text=f"На дорабтоку",
                                                callback_data='rework' + str(i['id']))
                    kb_pass = types.InlineKeyboardButton(text=f"Сдан",
                                                callback_data='passed' + str(i['id']))
                    kb.add(kb_check, kb_def, kb_adm, kb_pass)
                bot.send_message(message.chat.id,f"{j['surname']} {j['group_study']}", reply_markup=kb)
    else:
        bot.send_message(message.chat.id, 'Никто не сдал. Пока что..')




@bot.message_handler(commands=['study'])

def start_study(message):
    if db.check_student(message.from_user.id):
        student_group = db.select_info(data = 'group_study', table='students', column='user_id', value=message.from_user.id)[0][0]
        if db.check_disp_student(student_group):
            disciplines = db.select_info(data='discipline_name', table='disciplines', column='group_study', value=student_group)
            disciplines_id = db.select_info(data='id', table='disciplines', column='group_study', value=student_group)
            ds_name = []
            ds_id = []
            for i in disciplines:
                ds_name.append(i[0])
            for i in disciplines_id:
                ds_id.append(i[0])

            disciplines_dict = dict(zip(ds_id, ds_name))

            kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            kb_disp = [types.KeyboardButton(text=x) for x in list(disciplines_dict.values())]
            kb.add(*kb_disp)
            msg = bot.send_message(message.chat.id,
                                   f'Дисциплины для группы {student_group} загружены! Выберите дисциплину',
                                   reply_markup=kb)
            bot.register_next_step_handler(msg, some_action, disciplines_dict)


def some_action(message, disciplines_dict):
    for k, v in disciplines_dict.items():
        if message.text == v:
            ds_id = k
    kb = types.InlineKeyboardMarkup(row_width=1)
    if not db.check_get_disp_to_check(message.from_user.id, ds_id):
        kb_1= types.InlineKeyboardButton(text=f"Сдан на проверку", callback_data='sendcheck' + str(ds_id) + " " + str(message.from_user.id))
    else:

        kb_1 = types.InlineKeyboardButton(text="Статус", callback_data='status' + str(ds_id) + " " + str(message.from_user.id))
    kb.add(kb_1)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=kb)




@bot.callback_query_handler(func = lambda call: True)

def send_check(call):
    if call.data.startswith('sendcheck'):
        callback = call.data.split()
        id = callback[0].replace('sendcheck', '')
        ds_idtut = db.cur.execute(f"""SELECT tutor FROM disciplines WHERE id = '{id}'""").fetchone()[0]
        ds_stgr = db.cur.execute(f"""SELECT group_study FROM students WHERE user_id = '{str(callback[1])}'""").fetchone()[0]
        db.add_to_check(callback[1], id, ds_stgr, ds_idtut)
        bot.send_message(call.message.chat.id, 'Ожидайте результат')

    elif call.data.startswith('on_check'):
        callback = call.data.split()
        id = callback[0].replace('on_check', '')
        db.update_to_check(int(id), check='on_check')
        bot.send_message(call.message.chat.id, 'ОК')

    elif call.data.startswith('admwork'):
        callback = call.data.split()
        id = callback[0].replace('admwork', '')
        db.update_to_check(int(id), check='admwork')
        bot.send_message(call.message.chat.id, 'ОК')

    elif call.data.startswith('rework'):
        callback = call.data.split()
        id = callback[0].replace('rework', '')
        db.update_to_check(int(id), check='rework')
        bot.send_message(call.message.chat.id, 'ОК')

    elif call.data.startswith('passed'):
        callback = call.data.split()
        id = callback[0].replace('passed', '')
        db.update_to_check(int(id), check='passed')
        bot.send_message(call.message.chat.id, 'ОК')

    elif call.data.startswith('status'):
        callback = call.data.split()
        id = callback[0].replace('status', '')
        with db.con:
            get_info = db.cur.execute(f"""SELECT * FROM check_att WHERE student_id ='{callback[1]}' AND discipline_id = '{id}'""").fetchall()
            get_info_ds = db.cur.description
        get_info_dict = [dict(zip([col[0] for col in get_info_ds], row)) for row in get_info]
        answer =''
        for i in get_info_dict:
            if i['on_check'] == 'True':
                answer = 'Принят на проверку'
            elif i['rework'] == 'True':
                answer = 'На доработку'
            elif i['admittance'] == 'True':
                answer = 'К защите'
            elif i['passed'] == 'True':
                answer = 'Сдан!'
            else:
                answer = 'Преподаватель еще не принял'
        bot.send_message(call.message.chat.id, answer)


bot.polling(none_stop=True)