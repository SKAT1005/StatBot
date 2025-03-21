import hashlib
import hmac
import json
import os
import urllib.parse
from collections import OrderedDict
from collections.abc import MutableMapping
from xml.sax import parse

from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app.models import Manager, Bots, Link, Order
from const import bot


def login_register(request):
    """
    Отображает страницу авторизации/регистрации и обрабатывает формы (без Django Forms).
    """
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        if 'login_submit' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(username=email, password=password) # Authenticate using email as username
            if user is not None:
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему!")
                return redirect('home')
            else:
                messages.error(request, "Неверный email или пароль.")

        elif 'register_submit' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Basic validation (you should add more robust validation)
            if not name or not email or not password:
                messages.error(request, "Пожалуйста, заполните все поля.")
            elif Manager.objects.filter(username=email).exists(): # Check if email exists as username
                messages.error(request, "Пользователь с таким email уже зарегистрирован.")
            else:
                try:
                    user = Manager.objects.create_user(username=email, email=email, password=password, first_name=name) # Use email as username
                    login(request, user) # Automatically log in the user after registration
                    messages.success(request, f"Аккаунт создан для {name}, вы вошли в систему.")
                    return redirect('bot_list') # Redirect to home after registration
                except Exception as e:
                    messages.error(request, f"Ошибка регистрации: {e}")

    return render(request, 'auth.html')



def logout_view(request):
    """
    Выход пользователя из системы.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Вы вышли из системы.")
    return redirect('')  # Перенаправить на страницу входа



# Пример домашней страницы (если вы перенаправляете на нее после входа)
def bot_list(request):
    if request.user.is_authenticated:
        user = request.user
        context = {'bots': user.bots.all(), 'user': user}
        return render(request, 'bot_list.html', context=context)
    else:
        return redirect('')


def bot_detail(request, pk):
    if request.user.is_authenticated:
        user = request.user
        bott = Bots.objects.filter(id=pk)
        if bott:
            bott = bott.first()
            links = Link.objects.filter(bot=bott)
            context = {'user': user, 'bot': bott, 'links':links}
            return render(request, 'bot_details.html', context=context)
        else:
            return redirect('bot_list')
    return redirect('')


def create_bot(request):
    """
    Представление для создания нового бота.
    """
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        product_name = request.POST.get('product_name')
        hello_message = request.POST.get('hello_message')
        channel = request.POST.get('channel')
        price = request.POST.get('price')
        month = request.POST.get('month')

        # Валидация данных (можно добавить более строгую валидацию)
        if not name or not hello_message or not channel or not price or not month or not product_name:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return render(request, 'create_bot.html')  # Замените 'create_bot.html' на имя вашего шаблона

        try:
            price = int(price)
            month = int(month)
        except ValueError:
            messages.error(request, "Цена и количество месяцев должны быть числами.")
            return render(request, 'create_bot.html')

        # Создание нового бота
        try:
            bot = Bots.objects.create(
                name=name,
                product_name=product_name,
                hello_message=hello_message,
                channel=channel,
                price=price,
                month=month
            )
            user.bots.add(bot)
            return redirect(reverse('bot_detail', kwargs={'pk': bot.pk}))
        except Exception as e:
            messages.error(request, f"Произошла ошибка при создании бота: {e}")
            return render(request, 'create_bot.html')

    return render(request, 'create_bot.html')




def create_link(request, pk):
    """
    Представление для создания нового бота.
    """
    user_bot = Bots.objects.get(id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return render(request, 'create_link.html')  # Замените 'create_bot.html' на имя вашего шаблона

        try:
            link = Link.objects.create(
                bot=user_bot,
                name=name,
            )
            link.link = f'https://t.me/{bot.get_me().username}?start={link.id}'
            link.save(update_fields=['link'])
            return redirect(reverse('bot_detail', kwargs={'pk': user_bot.pk}))
        except Exception as e:
            messages.error(request, f"Произошла ошибка при создании бота: {e}")
            return render(request, 'create_bot.html')


    return render(request, 'create_link.html', context={'bot': user_bot})


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

def parse_data(data):
    data = dict(data)
    print(data['order_id'])

@csrf_exempt  # Disable CSRF protection for this view (needed for webhooks)
def webhook_view(request):
    """
    Django view to handle webhook requests with HMAC verification.
    """
    secret_key = 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8'  # Get secret from env

    # Verify that the request is a POST request
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are allowed')

    # Get the signature from the headers
    signature = request.headers.get('Sign')
    if not signature:
        return HttpResponseBadRequest('Signature not found')

    # Read the request body
    request_body = request.body

    # Verify the signature
    try:
        request_body_dict = convert_string_to_json(request_body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON format')
    expected_signature = sign(request_body_dict, secret_key)

    if not hmac.compare_digest(expected_signature, signature):
        return HttpResponseForbidden('Signature is invalid')

    # Process the webhook data
    try:
        parse_data(request_body_dict) # Replace with your processing logic
        return HttpResponse('Webhook received and processed', status=200)
    except Exception as e:
        # Log the error
        print(f"Error processing webhook: {e}")  # Replace with proper logging
        return HttpResponse(f"Error processing webhook: {e}", status=500)

