import hashlib
import hmac
import json
import urllib.parse

from const import bot

# Секретный ключ. Можно найти на странице настроек,
# в личном кабинете платежной формы.
secret_key = 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8'
linktoform = 'https://artmeup.payform.ru/'


def calculate_hmac(data):
    """
    Вычисляет HMAC-подпись для данных.

    Args:
        data (dict): Словарь с данными для подписи.
        secret_key (str): Секретный ключ.

    Returns:
        str: HMAC-подпись в шестнадцатеричном формате.
    """
    message = json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    secret_key_encoded = secret_key.encode('utf-8')
    hmac_digest = hmac.new(secret_key_encoded, message, hashlib.sha256).hexdigest()
    return hmac_digest


def generate_link(order):
    data = {
        'order_id': f'{order.id}',
        'customer_phone': '+79027573093',
        'customer_email': 'slava2006tukin@yandex.ru',
        'products': [
            {
                'name': f'{order.link.bot.product_name}',
                'price': f'{int(order.link.bot.price)}',
                'quantity': '1',
            },
        ],
        'do': 'pay',
        'urlSuccess': f'https://t.me/{bot.get_me().username}',
        'npd_income_type': 'FROM_INDIVIDUAL',
        'demo_mode': 1
        # 'paid_content': 'Текс сообщения'
    }
    hmac_signature = calculate_hmac(data)
    url_params = {
        'data': json.dumps(data, separators=(',', ':'), ensure_ascii=False),
        'hmac': hmac_signature
    }
    redirect_url = linktoform + '?' + urllib.parse.urlencode(url_params)

    return redirect_url
