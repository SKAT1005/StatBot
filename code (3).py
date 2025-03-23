import urllib.parse
import json
import hmac
import hashlib
from collections import OrderedDict  # Важно для сохранения порядка ключей

import urllib.parse
import json
import hmac
import hashlib
from collections import OrderedDict  # Важно для сохранения порядка ключей


def convert_string_to_json(input_string):
    """
    Преобразует строку в формате URL encoded query string в JSON (OrderedDict).
    Сохраняет порядок ключей и корректно обрабатывает вложенные структуры данных,
    особенно массив products.

    Args:
        input_string: Строка, которую нужно преобразовать.  Должна быть bytes.

    Returns:
        OrderedDict, представляющий JSON, или None, если преобразование не удалось.
    """
    # Декодируем bytes строку в unicode строку
    decoded_string = input_string.decode('utf-8')
    decoded_string = urllib.parse.unquote(decoded_string).split('&')
    for i in range(len(decoded_string)):
        decoded_string[i] = decoded_string[i].replace('+7', ':Lm').replace('+', ' ').replace(':Lm', '+7')

    # Разбираем строку вручную, сохраняя порядок
    result_dict = {}
    products = []

    for item in decoded_string:
        key, value = item.split("=", 1)  # Разбиваем по первому вхождению '=', чтобы обрабатывать значения с '='
        key = key.strip()  # Удаляем лишние пробелы в начале и конце ключа
        value = value.strip() # Удаляем лишние пробелы в начале и конце значения

        if key.startswith("products["):
            # Обработка продуктов (products[0][name], products[0][price] и т.д.)
            parts = key.split("[")
            _, index_str, field_str = parts  # parts: ['products', '0]', 'name]']
            index = int(index_str[:-1])  # Убираем ']' и преобразуем в int
            field = field_str[:-1]  # убираем ']'

            if len(products) <= index:
                products.append({})

            products[index][field] = value
        else:
            result_dict[key] = value

    if products:
        result_dict["products"] = products

    return result_dict


def generate_signature(data, secret_key):
    message = json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    print("Message:", message.decode('utf-8'))  # Декодируем для печати
    expected_signature = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()
    return expected_signature


# Пример использования
input_string = b'date=2025-03-21T00%3A00%3A00%2B03%3A00&order_id=1&order_num=test&domain=artmeup.payform.ru&sum=1000.00&customer_phone=%2B79999999999&customer_email=email%40domain.com&customer_extra=%D1%82%D0%B5%D1%81%D1%82&payment_type=%D0%9F%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0%D1%8F+%D0%BA%D0%B0%D1%80%D1%82%D0%B0+Visa%2C+MasterCard%2C+%D0%9C%D0%98%D0%A0&commission=3.5&commission_sum=35.00&attempt=1&sys=test&products%5B0%5D%5Bname%5D=%D0%94%D0%BE%D1%81%D1%82%D1%83%D0%BF+%D0%BA+%D0%BE%D0%B1%D1%83%D1%87%D0%B0%D1%8E%D1%89%D0%B8%D0%BC+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B0%D0%BC&products%5B0%5D%5Bprice%5D=1000.00&products%5B0%5D%5Bquantity%5D=1&products%5B0%5D%5Bsum%5D=1000.00&payment_status=success&payment_status_description=%D0%A3%D1%81%D0%BF%D0%B5%D1%88%D0%BD%D0%B0%D1%8F+%D0%BE%D0%BF%D0%BB%D0%B0%D1%82%D0%B0'
secret_key = "b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8"  # Замените на ваш реальный секретный ключ

data = convert_string_to_json(input_string)

if data:
    signature = generate_signature(data, secret_key)
    print("Generated Signature:", signature)
else:
    print("Не удалось преобразовать строку в JSON.")
