
import hashlib
import hmac
import urllib.parse
import Telebot

# Секретный ключ. Можно найти на странице настроек,
# в личном кабинете платежной формы.
secret_key = '2y2aw4oknnke80bp1a8fniwuuq7tdkwmmuq7vwi4nzbr8z1182ftbn6p8mhw3bhz'
linktoform = 'https://demo.payform.ru/'

def create_hmac(data, secret_key):
    """Создает HMAC-подпись для данных."""
    message = '&'.join([f"{k}={v}" for k, v in sorted(data.items()) if k != 'signature']).encode('utf-8')
    secret = secret_key.encode('utf-8')
    hmac_digest = hmac.new(secret, message, hashlib.sha256).hexdigest()
    return hmac_digest

def generate_link(order):
    data = {
        'order_id': f'{order.id}',
        'products': [
            {

                # название товара - необходимо прописать название вашего товара
                #          (обязательный параметр)
                'name': f'{order.name}',

                # цена за единицу товара, 123 - значение, которое нужно прописать
                #      (обязательный параметр)
                'price': f'{order.price}',

                # количество товара, х - значение, которое нужно прописать
                #           (обязательный параметр)
                'quantity': '1',
            },
        ],
        'do': 'pay',
        'urlSuccess': 'https://demo.payform.ru/demo-success',
        'npd_income_type': 'FROM_INDIVIDUAL',
        #'paid_content': 'Текс сообщения'
    }

    data['signature'] = create_hmac(data, secret_key)

    link = f"{linktoform}?{urllib.parse.urlencode(data)}"

    print(link)


