

from create_pay_link import generate_payment_link
from telebot.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

def pay_murkup(order):
    markup = InlineKeyboardMarkup()
    link = generate_payment_link(order)
    pay = InlineKeyboardButton('Оплатить', web_app=WebAppInfo(link)) #web_app=WebAppInfo(link))
    markup.add(pay)
    return markup


def invite(link):
    markup = InlineKeyboardMarkup()
    invite_link = InlineKeyboardButton('Ссылка для вступления в канал', url=link)
    markup.add(invite_link)
    return markup