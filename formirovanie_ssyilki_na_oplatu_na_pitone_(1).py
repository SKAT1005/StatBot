from collections.abc import MutableMapping
from urllib.parse import urlencode

from const import bot


def generate_payment_link():

    linktoform = 'https://artmeup.payform.ru/'
    secret_key = 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8'

    data = {
        # хххх - номер заказ в системе интернет-магазина
        'order_id': 12,

        # перечень товаров заказа
        'products': [
            {
                'name': 'Товар 1',
                'price': '123',
                'quantity': '1',
            },
        ],

        'do': 'pay',
        'urlReturn' : f'https://t.me/{bot.get_me().username}',
        'urlSuccess': f'https://t.me/{bot.get_me().username}',
        'urlNotification': 'https://slavishly-prospering-drake.cloudpub.ru/webhook',
        'discount_value': 0.00,
        'npd_income_type': 'FROM_INDIVIDUAL',
    }
    # подписываем с помощью кастомной функции sign (см ниже)
    data['signature'] = sign(data, secret_key)

    # компануем ссылку с помощью кастомной функции http_build_query (см ниже)
    link = linktoform + '?' + urlencode(http_build_query(data))

    return link

def sign(data, secret_key):
    import hashlib
    import hmac
    import json

    # переводим все значения data в string c помощью кастомной функции deep_int_to_string (см ниже)
    deep_int_to_string(data)

    # переводим data в JSON, с сортировкой ключей в алфавитном порядке, без пробелом и экранируем бэкслеши
    data_json = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).replace("/", "\\/")

    # создаем подпись с помощью библиотеки hmac и возвращаем ее
    return hmac.new(secret_key.encode('utf8'), data_json.encode('utf8'), hashlib.sha256).hexdigest()

def deep_int_to_string(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, MutableMapping):
            deep_int_to_string(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            for k, v in enumerate(value):
                deep_int_to_string({str(k): v})
        else: dictionary[key] = str(value)
                
def http_build_query(dictionary, parent_key=False):
    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + '[' + key + ']' if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(http_build_query(value, new_key).items())
        elif isinstance(value, list) or isinstance(value, tuple):
            for k, v in enumerate(value):
                items.extend(http_build_query({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)



n = generate_payment_link()

print(n)