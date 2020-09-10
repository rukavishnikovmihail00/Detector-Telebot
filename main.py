import telebot
import cv2
import random
import os
from telebot import types
import config

token = config.token
bot = telebot.TeleBot(token)


    

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,"Привет, {0.first_name}!\nЯ - бот, который может обнаружить лица на фотографии".format(message.from_user, bot.get_me()))
    bot.send_message(message.chat.id, "Напиши /help, если захочешь открыть список команд")
    bot.send_message(message.chat.id, "/info - узнать информацию об авторе")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти лица на фотографии")
    item2 = types.KeyboardButton("Распознать объект")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)


@bot.message_handler(commands=['help'])
def support(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти лица на фотографии")
    item2 = types.KeyboardButton("Распознать объект")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, "Вот что я могу сделать для тебя:" + "\n" + "(открой встроенную клавиатуру)", reply_markup=markup)

@bot.message_handler(commands=['info'])
def showInfo(message):
    bot.send_message(message.chat.id, "ВК: vk.com/rukavihnikov_mishka" + "\n" +  "Inst: rukavishn1kov" + "\n" +
                     "Email: rukavishnikovmihail00@yandex.ru" + "\n" + "GitHub:https://github.com/rukavishnikovmihail00/Detector-Telebot")

@bot.message_handler(content_types=['document'])
def sayMessage(message):
    bot.send_message(message.chat.id, "Нужно отправить фото не документом")

@bot.message_handler(content_types=['text'])
def botAnswer(message):
    if message.text == 'Найти лица на фотографии':
        msg = bot.send_message(message.chat.id, "Тогда пришли мне фото с людьми")
        bot.register_next_step_handler(msg, processPhoto)
    elif message.text == 'Распознать объект':
        msg = bot.send_message(message.chat.id, "Присылай!")
        bot.register_next_step_handler(msg, objClassifier)

    else:
        bot.send_message(message.chat.id, 'Я не понял, что ты от меня хочешь')

@bot.message_handler(content_types=['photo'])
def processPhoto(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path = file_info.file_path
        print(path)
        path = path[7:]
        temp = path
        print(path)   
        src=''+ path
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message,"Фото обрабатывается, еще секунду...")
    except Exception:
        bot.reply_to(message, "У меня что-то пошло не так, попробуй еще раз")


    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    image = cv2.imread(src)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(25, 25))

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

    name = random.randint(0,10000000)
    path = str(name) + '.png'
    cv2.imwrite(path , image)
    bot.send_photo(message.chat.id, open(path, 'rb'))
    os.remove(path)
    os.remove(temp)


@bot.message_handler(content_types=['photo'])
def objClassifier(message):
    print("Классификатор")
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path = file_info.file_path
        print(path)
        path = path[7:]
        temp = path
        print(path)   
        src=''+ path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message,"Фото обрабатывается, еще секунду...")
    except Exception:
        bot.reply_to(message, "У меня что-то пошло не так, попробуй еще раз")

    thres = 0.5
    classNames = []
    classFile = 'coco.names'
    with open(classFile, 'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')

    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = 'frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath, configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    img = cv2.imread(src)
    classIds, confs, bbox = net.detect(img, confThreshold=thres)
    if(len(classIds)) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            cv2.rectangle(img, box, color=(0,255,0), thickness=2)
            cv2.putText(img, classNames[classId-1].upper(), (box[0]+10, box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.putText(img, str(round(confidence*100))+'%', (box[0]+200, box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
    name = random.randint(0,10000000)
    path = str(name) + '.png'
    cv2.imwrite(path , img)
    bot.send_photo(message.chat.id, open(path, 'rb'))
    os.remove(path)
    os.remove(temp)

bot.polling(none_stop=True)
