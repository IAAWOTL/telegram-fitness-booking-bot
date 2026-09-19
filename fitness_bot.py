import telebot
import os
from dotenv import load_dotenv
from telebot import types
from pathlib import Path

load_dotenv()
project_folder = Path(__file__).resolve().parent


my_secret = os.getenv("TELEGRAM_KEY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))
bot = telebot.TeleBot(my_secret)

exercises = {
    'Кардио': 1000,
    'Силовая тренировка': 2000,
    'Йога': 1500,
    'Растяжка': 1200,
    }

user_data = {}


def start_handler(message):
  """Функция для обработки команды /start"""
  user_data.pop(message.chat.id, None)
  welcome_message = 'Добро пожаловать!'
  bot.send_message(message.chat.id, welcome_message)
  show_exercises_menu(message)


def show_exercises_menu(message):
  """Функция для отображения меню с тренировками"""
  markup = types.InlineKeyboardMarkup()
  for exercise, price in exercises.items():
    button_text = f'{exercise} - {price} руб.'
    markup.add(types.InlineKeyboardButton(button_text, callback_data=exercise))
  bot.send_message(message.chat.id,
                   'Пожалуйста, выберите тренировку:',
                   reply_markup=markup
                   )


def exercise_selected(call):
  """Обработчик выбора вида тренировки"""
  bot.answer_callback_query(call.id)
  exercise = call.data
  user_data[call.message.chat.id] = {'exercise': exercise}
  bot.send_message(call.message.chat.id, f'Вы выбрали - {exercise}'
                   '\nДля записи на тренировку, введите ваш номер телефона:'
                   )
  bot.register_next_step_handler(call.message, get_phone_number)


def get_phone_number(message):
  """Функция для запроса номера телефона"""
  phone_number = message.text

  if phone_number.strip() == "":
    bot.send_message(message.chat.id, "Повторите, пожалуйста, ввод номера")
    bot.register_next_step_handler(message, get_phone_number)
    return
  
  user_data[message.chat.id]['phone_number'] = phone_number.strip()
  bot.send_message(message.chat.id, 'Введите желаемую дату и '
                   'время для занятия:'
                   )
  bot.register_next_step_handler(message, get_date_time)


def send_image(chat_id):
  """Функция отправки изображения (памятки)"""
  image_path = project_folder / 'assets' / 'pamyatka.jpg'
  bot.send_message(chat_id, 'Ознакомьтесь, пожалуйста, с памяткой о '
                   'подготовке к тренировке.'
                   )
  with open(image_path, 'rb') as image:
    bot.send_photo(chat_id, image)


def get_date_time(message):
  """Функция для запроса даты и времени"""
  date_time = message.text.strip()

  if date_time == "":
    bot.send_message(message.chat.id, "Повторите, пожалуйста, ввод даты и "
                     "времени"
                     )
    bot.register_next_step_handler(message, get_date_time)
    return

  user_data[message.chat.id]['date_time'] = date_time
  exercise = user_data[message.chat.id]['exercise']
  phone_number = user_data[message.chat.id]['phone_number']
  bot.send_message(message.chat.id, 'Спасибо! Вы хотите записаться на '
                   f'{exercise} на {date_time}\nЯ свяжусь с вами по номеру '
                   f'{phone_number} для уточнения возможности записи.'
                   )
  bot.send_message(ADMIN_USER_ID, f'Новая запись:\nТренировка: {exercise}'
                   f'\nДата и время: {date_time}\nТелефон: {phone_number}'
                   )
  send_image(message.chat.id)  # Вызов функции отправки изображения (памятки)
  user_data.pop(message.chat.id, None)


# Регистрация обработчика для команды /start
bot.register_message_handler(start_handler, commands=['start'])
# Регистрация обработчика событий
bot.register_callback_query_handler(exercise_selected,
                                    func=lambda call:
                                    call.data in exercises.keys()
                                    )

# Запуск бота
bot.infinity_polling(none_stop=True)