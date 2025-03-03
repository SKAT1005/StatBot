

from create_pay_link import generate_link
from telebot.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

def pay_murkup(order):
    markup = InlineKeyboardMarkup()
    pay = InlineKeyboardButton('Оплатить', web_app=WebAppInfo(generate_link(order)))
    markup.add(pay)
    return markup


def invite(link):
    markup = InlineKeyboardMarkup()
    invite_link = InlineKeyboardButton('Ссылка для вступления в канал', url=link)
    markup.add(invite_link)
    return markup