import telebot
import os
from typing import Type
from random import randint
from filters import Filter  # BlueFilter, GreenFilter, InverseFilter, RedFilter
from filters import DolgovBlurFilter, SopolevRandomFilter, BekrenevReversFilter, KirpichevRedFilter, OrlovGreenFilter, BuninEdgesFilter
from PIL import Image
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Message
from main import token

bot = telebot.TeleBot(token)

filters: dict[str, Type[Filter]] = {
    "Рандом от Александра": SopolevRandomFilter(),
    "Блюр от Данилы": DolgovBlurFilter(),
    "ЧБ-реверс от Егора": BekrenevReversFilter(),
    "Красная маска от Захара": KirpichevRedFilter(),
    "Зеленая маска от Кирилла": OrlovGreenFilter(),
    "Рельеф от Николая": BuninEdgesFilter()
    }



user_images = {}
images_folder = "./images"
if not os.path.exists(images_folder):
    os.makedirs(images_folder)

@bot.message_handler(commands=['start'])
def keyboard_main(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Кнопка 1")
    button1 = telebot.types.KeyboardButton(text="Выход")
    button2 = telebot.types.KeyboardButton(text="Переход на Вторую страницу")
    button3 = telebot.types.KeyboardButton(text="Фоторедактор")
    keyboard.add(button_support, button1, button2, button3)
    bot.send_message(chat_id,'Привет, я MegaBot!!!',reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Переход на Вторую страницу')
def welcoddme(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Кнопка 1")
    button1 = telebot.types.KeyboardButton(text="Выход")
    button2 = telebot.types.KeyboardButton(text="Вернуться на главную")
    button3 = telebot.types.KeyboardButton(text="Кнопка 3")
    keyboard.add(button_support, button1, button2, button3)
    bot.send_message(chat_id,"Вы перешли на вторую страницу",reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Выход")
def remove_keyboard(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(chat_id,'Удаляю клавиатуру',reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Вернуться на главную")
def return_to_main_keyboard(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Написать в поддержку")
    button1 = telebot.types.KeyboardButton(text="Выход")
    button2 = telebot.types.KeyboardButton(text="Переход на Вторую страницу")
    button3 = telebot.types.KeyboardButton(text="Фоторедактор")
    keyboard.add(button_support, button1, button2, button3)
    bot.send_message(chat_id, 'Вы вернулись на главную клавиатуру', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Фоторедактор')
def handle_start(message: Message):
    bot.send_message(
        message.chat.id,
        "Я бот, который накладывает фильтры на картинки. Пожалуйста, загрузите изображение.",
    )

@bot.message_handler(content_types=["photo"])
def handle_photo(message: Message):
    process_image(message)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    apply_filter(message)


def process_image(message: Message):
    """Обработка изображений"""

    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded_file = bot.download_file(file_info.file_path)

    if not os.path.isdir(f"{images_folder}/{message.chat.id}"):
        os.mkdir(f"{images_folder}/{message.chat.id}")
    file_path = f"{images_folder}/{message.chat.id}/{str(randint(0, 1000001))}.jpg"

    with open(file_path, "wb") as image_file:
        image_file.write(downloaded_file)

    user_images[message.chat.id] = file_path

    keyboard = make_filter_options_keyboard(message)
    button2 = telebot.types.KeyboardButton(text="Вернуться на главную")
    keyboard.add(button2)
    bot.send_message(message.chat.id, "Выберите фильтр:", reply_markup=keyboard)

def make_filter_options_keyboard(message: Message):
    """Собирает меню с кнопками-названиями фильтров"""
    markup = ReplyKeyboardMarkup(row_width=1)
    filter_buttons = [KeyboardButton(filt_name) for filt_name in filters.keys()]
    markup.add(*filter_buttons)
    return markup


def apply_filter(message: Message):
    """Применение выбранного фильтра и отправка результата.
    Обработка текстовых сообщений"""

    file_path = user_images.get(message.chat.id)
    if not file_path:
        bot.reply_to(
            message, "Изображение не найдено. Пожалуйста, загрузите изображение."
        )
        return

    try:
        img = Image.open(file_path)
    except IOError:
        # Ошибка считывания файла
        bot.reply_to(
            message,
            "Формат изображения не поддерживается. Пожалуйста, загрузите другое изображение.",
        )
        return

    selected_filter_name = message.text
    if selected_filter_name not in filters:
        bot.reply_to(
            message,
            "Выбранный фильтр не найден. Пожалуйста, выберите фильтр из предложенного списка.",
        )
        return

    try:
        selected_filter = filters[selected_filter_name]
        img = selected_filter.apply_to_image(img)

        img.save(file_path, "JPEG")

        with open(file_path, "rb") as image_file:
            bot.send_photo(message.chat.id, photo=image_file)
            bot.send_message(
                message.chat.id, "Ваше изображение с примененным фильтром."
            )

    except Exception as e:
        print(e)
        bot.reply_to(message, "Что-то пошло не так. Пожалуйста, попробуйте еще раз.")




bot.polling()
