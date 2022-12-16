import telebot
from telebot import types
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from bob_telegram_tools.bot import TelegramBot
from src.globals import Graphs

token = ''
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    bt1 = types.KeyboardButton('/choose_graph_type')
    bt2 = types.KeyboardButton('/build_graph')
    bt3 = types.KeyboardButton('/input')
    bt4 = types.KeyboardButton('/set_parameters')
    kb.add(bt1, bt2, bt3, bt4)
    bot.send_message(message.chat.id, 'Меню', reply_markup=kb)

@bot.message_handler(commands= ['choose_graph_type'])
def graph_type(message):
    kb1 = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Линейная зависимость', callback_data='line')
    bt2 = types.InlineKeyboardButton('Круговая диаграмма', callback_data='diagram')
    bt3 = types.InlineKeyboardButton('Гистограмма', callback_data='hist')
    bt4 = types.InlineKeyboardButton('Scatter', callback_data='dots')
    bt5 = types.InlineKeyboardButton('Столбчатая диаграмма', callback_data='stolb')
    kb1.add(bt1, bt2, bt3, bt4, bt5)
    bot.send_message(message.chat.id, 'Выберите тип графика', reply_markup=kb1)

@bot.message_handler(commands= ['set_parameters'])
def parameters_type(message):
    kb2 = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('Цвет графика', callback_data='col')
    bt2 = types.InlineKeyboardButton('Границы по x', callback_data='limits_x')
    bt3 = types.InlineKeyboardButton('Границы по y', callback_data='limits_y')
    bt4 = types.InlineKeyboardButton('Подпись', callback_data='note')
    bt5 = types.InlineKeyboardButton('Количество столбцов', callback_data='columns')
    kb2.add(bt1, bt2, bt3, bt4, bt5)
    bot.send_message(message.chat.id, 'Измените параметр', reply_markup=kb2)

@bot.callback_query_handler(func=lambda call:True)
def call_back(call):
    default_types = ['line', 'diagram', 'hist', 'dots', 'stolb']
    if call.data in default_types:
        Graphs.graph_type = call.data
        bot.send_message(call.message.chat.id, 'График выбран')
    else:
        global min_x, max_x, min_y, max_y, colour
        # chat_id = message.chat.id
        if call.data == 'limits_x':
            msg = bot.send_message(call.message.chat.id, 'Введите ограничение по x')
            bot.register_next_step_handler(msg, getpar1)
        elif call.data == 'limits_y':
            msg = bot.send_message(call.message.chat.id, 'Введите ограничение по y')
            bot.register_next_step_handler(msg, getpar2)
        elif call.data == 'col':
            msg = bot.send_message(call.message.chat.id, 'Введите цвет')
            bot.register_next_step_handler(msg, getcolour)
        elif call.data == 'note':
            msg = bot.send_message(call.message.chat.id, 'Введите подпись')
            bot.register_next_step_handler(msg, get_title)
        elif call.data == 'columns':
            msg = bot.send_message(call.message.chat.id, 'Введите количество столбцов')
            bot.register_next_step_handler(msg, get_column)

def getpar1(message):
    Graphs.border_x = message.text.split()
    bot.send_message(message.chat.id, 'Границы по x установлены')

def getpar2(message):
    Graphs.border_y = message.text.split()
    bot.send_message(message.chat.id, 'Границы по y установлены')
def getcolour(message):
    Graphs.col = message.text
    bot.send_message(message.chat.id, 'Цвет установлен')
def get_title(message):
    Graphs.note = message.text
    bot.send_message(message.chat.id, 'Подпись выбрана')

@bot.message_handler(commands=['input'])
def user_answer(message):
    send_x = bot.send_message(message.chat.id, "Введите данные(координаты абсциссы")
    bot.register_next_step_handler(send_x, input_x)

def input_x(message):
    Graphs.list_x = message.text.split()
    send_y = bot.send_message(message.chat.id, "координаты ординаты")
    bot.register_next_step_handler(send_y, input_y)

def input_y(message):
    Graphs.list_y = message.text.split()
    bot.send_message(message.chat.id, 'Данные введены')
def get_column(message):
    Graphs.columns = message.text.split()
    bot.send_message(message.chat.id, 'Данные получены')

def linar_graph(id):
    client = TelegramBot(token, id)
    arr_x = np.array(Graphs.list_x, dtype=float)
    arr_y = np.array(Graphs.list_y[:len(Graphs.list_x)], dtype=float)
    mx = arr_x.sum() / len(Graphs.list_x)
    my = arr_y.sum() / len(Graphs.list_x)
    a2 = np.dot(arr_x, arr_x) / len(Graphs.list_x)
    a11 = np.dot(arr_x, arr_y) / len(Graphs.list_x)

    kk = (a11 - mx * my) / (a2 - mx ** 2)
    bb = my - kk * mx
    if len(Graphs.border_x) == 2:
        plt.xlim(int(Graphs.border_x[0]), int(Graphs.border_x[1]))
    if len(Graphs.border_y) == 2:
        plt.ylim(int(Graphs.border_y[0]), int(Graphs.border_y[1]))
    plt.scatter(arr_x, arr_y, c='red')
    plt.grid(True)
    if len(Graphs.border_x) == 2:
        Graphs.list_x.append(Graphs.border_x[0])
        Graphs.list_x.append(Graphs.border_x[1])
    newarr_x = np.array(Graphs.list_x, dtype=float)
    ff = np.array([kk * q + bb for q in newarr_x])
    if len(Graphs.note) > 0:
        plt.title(Graphs.note)
    if len(Graphs.col) > 0:
        plt.plot(newarr_x, ff, c=Graphs.col)
    else:
        plt.plot(newarr_x, ff, c='blue')
    client.send_plot(plt)
    client.clean_tmp_dir()
    plt.cla()
    if len(Graphs.border_x) == 2:
        Graphs.list_x.pop()
        Graphs.list_x.pop()

def diagram(id):
    client = TelegramBot(token, id)
    plt.pie(Graphs.list_x, labels=Graphs.list_y)
    if len(Graphs.note) > 0:
        plt.title(Graphs.note)
    client.send_plot(plt)
    client.clean_tmp_dir()
    plt.cla()

def histogram(id):
    client = TelegramBot(token, int(id))
    if len(Graphs.columns) > 0:
        new_list_x = []
        for i in range(len(Graphs.list_x)):
            new_list_x.append(round(float(Graphs.list_x[i])))
        data = np.array(new_list_x)
        processing = np.linspace(np.min(data), np.max(data), int(Graphs.columns[0]))
        bars = [len(data[np.bitwise_and(data >= processing[i], data < processing[i + 1])]) for i in
                range(len(processing) - 1)]
        points = np.arange(min(new_list_x), max(new_list_x),
                           (max(new_list_x) - min(new_list_x)) / (len(processing) - 1))
        plt.grid()
        plt.bar(points, bars, width=(max(new_list_x) - min(new_list_x)) / (len(processing) - 1))
        if len(Graphs.note) > 0:
            plt.title(Graphs.note)
        client.send_plot(plt)
        client.clean_tmp_dir()
        plt.cla()
    else:
        bot.send_message(id, 'сначала введите количество столбцов')

def scatter(id):
    client = TelegramBot(token, id)
    arr_x = np.array(Graphs.list_x, dtype=float)
    arr_y = np.array(Graphs.list_y[:len(Graphs.list_x)], dtype=float)
    if len(Graphs.col) > 0:
        plt.scatter(arr_x, arr_y, c=Graphs.col)
    else:
        plt.scatter(arr_x, arr_y, c='red')
    if len(Graphs.note) > 0:
        plt.title(Graphs.note)
    plt.grid()
    client.send_plot(plt)
    client.clean_tmp_dir()
    plt.cla()

def columns(id):
    client = TelegramBot(token, id)
    arr_x = np.array(Graphs.list_x, dtype=float)
    arr_y = np.array(Graphs.list_y[:len(Graphs.list_x)], dtype=float)
    if len(Graphs.col) > 0:
        plt.bar(arr_x, arr_y, color=Graphs.col)
    else:
        plt.bar(arr_x, arr_y, color='red')
    if len(Graphs.note) > 0:
        plt.title(Graphs.note)
    client.send_plot(plt)
    client.clean_tmp_dir()
    plt.cla()


@bot.message_handler(commands=['build_graph'])
def build(message):
    matplotlib.use('agg')
    if Graphs.list_x and Graphs.list_y:
        if Graphs.graph_type == 'line':
            linar_graph(int(message.chat.id))
        elif Graphs.graph_type == 'diagram':
            diagram(int(message.chat.id))
        elif Graphs.graph_type == 'hist':
            histogram(message.chat.id)
        elif Graphs.graph_type == 'dots':
            scatter(int(message.chat.id))
        elif Graphs.graph_type == 'stolb':
            columns(int(message.chat.id))
    else:
        bot.send_message(message.chat.id, 'Сначала введите данные')
bot.polling()