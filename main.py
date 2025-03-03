import os

import django

from const import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PayUlimitedBot.settings')
django.setup()


from .app.models import Link, Order
import buttons



def hello_message(chat_id):
    bot.send_message(chat_id=chat_id, text='Приветственное сообщение для тех, кто зашел в бота')
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if message.text.split() > 1:
        try:
            link = Link.objects.get(id=message.text.split()[1])
        except Exception:
            hello_message(chat_id=chat_id)
        else:
            order = Order.objects.create(chat_id=chat_id, link=link)
            bot.send_message(chat_id=chat_id, text=link.bot.hello_message, reply_markup=buttons.pay_murkup(order))
    else:
        hello_message(chat_id=chat_id)


