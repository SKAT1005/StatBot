import hashlib
import hmac
import json
import os
import urllib.parse
from collections import OrderedDict

from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app.models import Manager, Bots, Link, Order
from buttons import invite
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
@csrf_exempt  # Disable CSRF protection for this view (needed for webhooks)
def webhook_view(request):
    """
    Django view to handle webhook requests with HMAC verification.
    """
    secret_key = os.environ.get('SECRET_KEY', 'b47792ff804f0e5cb982e6fe2844e1274c311b0b20675e4b8321132c9346b7e8')  # Get secret from env

    # Verify that the request is a POST request
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are allowed')

    # Get the signature from the headers
    signature = request.headers.get('Sign')
    if not signature:
        return HttpResponseBadRequest('Signature not found')

    # Read the request body
    request_body = request.body
    request_body_dict = convert_string_to_json(request_body)

    n = verify_hmac(request_body_dict, secret_key, signature)
    if not n:
        return HttpResponseForbidden('Signature is invalid')

    # Process the webhook data
    try:
        process_webhook_data(request_body_dict) # Replace with your processing logic
        return HttpResponse('Webhook received and processed', status=200)
    except Exception as e:
        # Log the error
        print(f"Error processing webhook: {e}")  # Replace with proper logging
        return HttpResponse(f"Error processing webhook: {e}", status=500)



def verify_hmac(data, secret_key, signature):
    """
    Verifies the HMAC signature of the provided data.

    Args:
        data: The data (usually a dictionary) that was signed.
        secret_key: The secret key used to generate the signature.
        signature: The signature to verify.

    Returns:
        True if the signature is valid, False otherwise.
    """
    message = json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    expected_signature = hmac.new(secret_key.encode('utf-8'), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def process_webhook_data(data):
    order = Order.objects.get(id=data['order_id'])
    if data['payment_status'] == 'success':
        link = bot.create_chat_invite_link(chat_id=order.link.bot.channel, member_limit=1, creates_join_request=False)
        bot.send_message(chat_id=order.chat_id, text='Оплата прошла успешно. Вы можете присоедениться к каналу', reply_markup=invite(link))

