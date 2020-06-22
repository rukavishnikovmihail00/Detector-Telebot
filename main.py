import telebot
import cv2
import random
import numpy as np
import time
import os
from telebot import types
token = "1222340645:AAEIYp5m5QaYQx68tQ2xo-P7ccA5xE27OEQ"

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привет, {0.first_name}!\nЯ - бот, который может обнаружить объект на фотографии".format(message.from_user, bot.get_me()))
    bot.send_message(message.chat.id, "Напиши /help, если захочешь открыть список команд")
    bot.send_message(message.chat.id, "/info - узнать информацию об авторе")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти объект на фотографии")
    markup.add(item1)
    bot.send_message(message.chat.id, "Что ты хочешь сделать?", reply_markup=markup)


@bot.message_handler(commands=['help'])
def support(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Найти объект на фотографии")
    markup.add(item1)
    bot.send_message(message.chat.id, "Вот что я могу сделать для тебя:", reply_markup=markup)

@bot.message_handler(commands=['info'])
def showInfo(message):
    bot.send_message(message.chat.id, "ВК: vk.com/rukavishnikov_mishka" + "\n" +  "Inst: rukavishn1kov" + "\n" +
                     "Email: rukavishnikovmihail00@yandex.ru" + "\n" + "GitHub:https://github.com/rukavishnikovmihail00/Detector-Telebot")

@bot.message_handler(content_types=['text'])
def botAnswer(message):
    if message.text == 'Найти объект на фотографии':
        bot.send_message(message.chat.id, "Тогда пришли мне фото")
    else:
        bot.send_message(message.chat.id, 'Я не понял, что ты от меня хочешь')

@bot.message_handler(content_types=['photo'])
def processPhoto(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src=''+file_info.file_path;
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message,"Фото обрабатывается, еще секунду...")
        print(src)
    except Exception:
        bot.reply_to(message, "У меня что-то пошло не так, попробуй еще раз")


    args = {'confidence': 0.5, 'threshold': 0.3}


    LABELS = ['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 
    'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
    'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 
    'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 
    'teddy bear', 'hair drier', 'toothbrush']

    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
        dtype="uint8")


    weightsPath = 'yolo-coco\yolov3.weights'
    configPath = 'yolo-coco\yolov3.cfg'


    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)


    image = cv2.imread(src)
    (H, W) = image.shape[:2]


    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()

    print("[INFO] YOLO took {:.6f} seconds".format(end - start))


    boxes = []
    confidences = []
    classIDs = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if confidence > args["confidence"]:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)


    idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
        args["threshold"])


    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)


    name = random.randint(0,10000000)
    path = 'photos/' + str(name) + '.png'
    cv2.imwrite(path , image)
    bot.send_photo(message.chat.id, open(path, 'rb'))
bot.polling(none_stop=True)
