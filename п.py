import telebot
import random
import json
from telebot import types
from main import token

bot = telebot.TeleBot(token)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content['questions'], content['answers_to_character'], content['results']

questions, answers_to_character, results = load_json('questions.json')

def load_user_data():
    try:
        with open('user_data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

def save_user_data():
    with open('user_data.json', 'w', encoding='utf-8') as file:
        json.dump(users_data, file, ensure_ascii=False, indent=4)

users_data = {}

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Доступные команды:\n""/start - начать анкету\n""/help - справка о доступных командах")
    url = "https://discordapp.com/users/909464722267590657/"
    text = f'Вот мой дискорд если что: <a href="{url}">Нажми здесь</a>'
    bot.send_message(message.chat.id, text, parse_mode='HTML')

def get_question_markup(question):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(*question['options'])
    return markup

def get_result(score):
    max_score = max(score.values())
    best_matches = [key for key, value in score.items() if value == max_score]

    if len(best_matches) > 1:
        result = random.choice(best_matches)
    else:
        result = best_matches[0]

    return result


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in users_data and 'current_question' in users_data[user_id]:
        bot.send_message(user_id, 'Продолжаем вашу предыдущую сессию.')
        send_question(user_id)
    else:
        bot.send_message(user_id,'🚨Осторожно! Этот тест исключительно субъективен и основан только на моём личном мнении.')
        users_data[user_id] = {
            'current_question': 0,
            'score': {'Блум': 0, 'Стелла': 0, 'Флора': 0, 'Муза': 0, 'Текна': 0, 'Лейла': 0, "Мистер Загадка": 0}
        }
        save_user_data()
        send_question(user_id)

def send_question(user_id):
    user = users_data[user_id]
    question = questions[user['current_question']]
    markup = get_question_markup(question)
    bot.send_message(user_id, question['text'], reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if user_id not in users_data:
        bot.send_message(user_id, 'Чтобы начать анкету, используй команду /start')
        return

    user = users_data[user_id]
    current_question_index = user['current_question']
    question = questions[current_question_index]

    if message.text not in question['options']:
        bot.send_message(user_id, 'Пожалуйста, выбери один из предложенных вариантов')
        return

    character = answers_to_character[current_question_index][message.text]
    user['score'][character] += 1
    user['score']["Мистер Загадка"] = 0
    save_user_data()
    user['current_question'] += 1
    if user['current_question'] < len(questions):
        send_question(user_id)
    else:
        result = get_result(user['score'])
        bot.send_message(user_id, results[result]['text'])
        bot.send_message(user_id, results[result]['description'])
        bot.send_photo(user_id, results[result]['image'])
        bot.send_message(message.chat.id, '🚨Повторяю этот тест никак не Охарактеризо́вывает вас это лишь моё субъективное мнение!', reply_markup=types.ReplyKeyboardRemove())
        del users_data[user_id]
save_user_data()

bot.polling()