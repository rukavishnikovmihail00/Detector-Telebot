import telebot
import cv2
import random
from telebot import types
token = "1222340645:AAEIYp5m5QaYQx68tQ2xo-P7ccA5xE27OEQ"
#token = "1207803148:AAFfo8WM4mlOFQ0i8NADFEltALEp7YDbk-E"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,"Привет, {0.first_name}!\nЯ - бот, который может обнаружить лица на фотографии".format(message.from_user, bot.get_me()))
    bot.send_message(message.chat.id, "Напиши /help, если захочешь открыть список команд")
    bot.send_message(message.chat.id, "/info - узнать информацию об авторе")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти лица на фотографии")
    markup.add(item1)
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)


@bot.message_handler(commands=['help'])
def support(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти лица на фотографии")
    markup.add(item1)
    bot.send_message(message.chat.id, "Вот что я могу сделать для тебя:" + "\n" + "(открой встроенную клавиатуру)", reply_markup=markup)

@bot.message_handler(commands=['info'])
def showInfo(message):
    bot.send_message(message.chat.id, "ВК: vk.com/rukavihnikov_mishka" + "\n" +  "Inst: rukavishn1kov" + "\n" +
                     "Email: rukavishnikovmihail00@yandex.ru" + "\n" + "GitHub:https://github.com/rukavishnikovmihail00/Detector-Telebot")

@bot.message_handler(content_types=['text'])
def botAnswer(message):
    if message.text == 'Найти лица на фотографии':
        bot.send_message(message.chat.id, "Тогда пришли мне фото с людьми")
    else:
        bot.send_message(message.chat.id, 'Я не понял, что ты от меня хочешь')

@bot.message_handler(content_types=['photo'])
def processPhoto(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Костыль
        path = file_info.file_path
        arr = list(path)
        arr.remove('p')
        arr.remove('h')
        arr.remove('o')
        arr.remove('t')
        arr.remove('o')
        arr.remove('s')
        arr.remove('/')
        new_path = ''.join(arr)
        print(new_path)      
        src=''+new_path
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message,"Фото обрабатывается, еще секунду...")
        print(src)
    except Exception:
        bot.reply_to(message, "У меня что-то пошло не так, попробуй еще раз")


    # Processing photo
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    image = cv2.imread(src)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(20, 20))

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

    name = random.randint(0,10000000)
    path = str(name) + '.png'
    cv2.imwrite(path , image)
    bot.send_photo(message.chat.id, open(path, 'rb'))
bot.polling(none_stop=True)
