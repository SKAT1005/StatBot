import json
import urllib.parse

import urllib.parse
import json
import hmac
import hashlib
from collections import OrderedDict  # Важно для сохранения порядка ключей
from collections.abc import MutableMapping


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
    try:
        # Декодируем bytes строку в unicode строку
        decoded_string = input_string.decode('utf-8')

        # Используем urllib.parse.parse_qs для разбора строки запроса URL
        parsed_data = urllib.parse.parse_qs(decoded_string, keep_blank_values=True)

        # Преобразуем значения списков в отдельные значения, если список содержит только один элемент
        # и сохраняем порядок ключей
        ordered_data = OrderedDict()
        for key in urllib.parse.parse_qsl(decoded_string, keep_blank_values=True):  # Сохраняем порядок!
            if key[0] in parsed_data:
                value = parsed_data[key[0]]
                if len(value) == 1:
                    ordered_data[key[0]] = value[0]  # Преобразуем список из одного элемента в сам элемент
                else:
                    ordered_data[key[0]] = value

        # Обрабатываем вложенную структуру 'products'
        products = []
        product_keys = {}
        for key, value in list(ordered_data.items()):  # Итерируемся по копии ключей, чтобы можно было удалять ключи
            if 'products' in key:
                # Разбираем ключ, чтобы определить индекс продукта и название поля
                parts = key.split('[')
                if len(parts) >= 3:  # Проверяем, что ключ имеет правильную структуру
                    index = int(parts[1].replace(']', ''))
                    field = parts[2].replace(']', '')

                    # Создаем словарь продукта, если он еще не существует
                    if index not in product_keys:
                        product_keys[index] = OrderedDict()  # OrderedDict для сохранения порядка полей продукта

                    product_keys[index][field] = value

                    del ordered_data[key]  # Удаляем ключ, чтобы не мешал дальнейшей обработке

        # Преобразуем словарь индексов в список продуктов
        for index in sorted(product_keys.keys()):
            # Гарантируем определенный порядок полей внутри каждого продукта
            product = OrderedDict()
            product['name'] = product_keys[index].get('name')
            product['price'] = product_keys[index].get('price')
            product['quantity'] = product_keys[index].get('quantity')
            product['sum'] = product_keys[index].get('sum')
            products.append(product)

        if products:
            ordered_data['products'] = products

        return ordered_data
    except Exception as e:
        print(f"Ошибка при преобразовании в JSON: {e}")
        return None

def sign(data, secret_key):
    import hashlib
    import hmac
    import json
    deep_int_to_string(data)
    data_json = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).replace("/", "\\/")
    return hmac.new(secret_key.encode('utf8'), data_json.encode('utf8'), hashlib.sha256).hexdigest()

def deep_int_to_string(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, MutableMapping):
            deep_int_to_string(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            for k, v in enumerate(value):
                deep_int_to_string({str(k): v})
        else: dictionary[key] = str(value)

secret_key = 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8'
encoded_data = b'date=2025-03-21T00%3A00%3A00%2B03%3A00&order_id=1&order_num=test&domain=artmeup.payform.ru&sum=1000.00&customer_phone=%2B79999999999&customer_email=email%40domain.com&customer_extra=%D1%82%D0%B5%D1%81%D1%82&payment_type=%D0%9F%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0%D1%8F+%D0%BA%D0%B0%D1%80%D1%82%D0%B0+Visa%2C+MasterCard%2C+%D0%9C%D0%98%D0%A0&commission=3.5&commission_sum=35.00&attempt=1&sys=test&products%5B0%5D%5Bname%5D=%D0%94%D0%BE%D1%81%D1%82%D1%83%D0%BF+%D0%BA+%D0%BE%D0%B1%D1%83%D1%87%D0%B0%D1%8E%D1%89%D0%B8%D0%BC+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B0%D0%BC&products%5B0%5D%5Bprice%5D=1000.00&products%5B0%5D%5Bquantity%5D=1&products%5B0%5D%5Bsum%5D=1000.00&payment_status=success&payment_status_description=%D0%A3%D1%81%D0%BF%D0%B5%D1%88%D0%BD%D0%B0%D1%8F+%D0%BE%D0%BF%D0%BB%D0%B0%D1%82%D0%B0'

parsed_dict = convert_string_to_json(encoded_data)

print(sign(parsed_dict, secret_key))
