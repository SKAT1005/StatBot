
import hashlib
import hmac
import urllib.parse

# Секретный ключ. Можно найти на странице настроек,
# в личном кабинете платежной формы.
secret_key = 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8'
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


