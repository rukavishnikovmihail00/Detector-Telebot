import telebot
import cv2
import random
token = "1222340645:AAEIYp5m5QaYQx68tQ2xo-P7ccA5xE27OEQ"

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,"Привет, {0.first_name}!\nЯ - бот, который может обнаружить лица на фотографии".format(message.from_user, bot.get_me()))



@bot.message_handler(content_types=['photo'])
def processPhoto(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src=''+file_info.file_path;
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        bot.reply_to(message,"Фото добавлено")
        print(src)
    except Exception:
        bot.reply_to(message, "Я не смог добавить фото")


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
    path = 'photos/' + str(name) + '.png'
    cv2.imwrite(path , image)
    bot.send_photo(message.chat.id, open(path, 'rb'))

bot.polling(none_stop=True)
