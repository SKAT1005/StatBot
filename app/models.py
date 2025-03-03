from django.contrib.auth.models import AbstractUser
from django.db import models


class Manager(AbstractUser):
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0)
    bots = models.ManyToManyField('Bots', blank=True, verbose_name='боты')

    is_friend = models.BooleanField(default=False, verbose_name='Является ли сотрудником отдела заботы?')



class Bots(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название бота')
    product_name = models.CharField(max_length=128, verbose_name='Название продукта')
    channel = models.CharField(max_length=128, verbose_name='ID канала')
    month = models.IntegerField(default=1 , verbose_name='Сколько месяцев длится подписка')
    hello_message = models.CharField(max_length=2048, verbose_name='Приветственное сообщение')
    hello_photo = models.ImageField(blank=True, null=True, verbose_name='Приветственное фото')
    price = models.IntegerField(verbose_name='Цена подписки')
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0)



class Link(models.Model):
    bot = models.ForeignKey('Bots', on_delete=models.CASCADE, related_name='links', verbose_name='Бот')
    name = models.CharField(max_length=128, verbose_name='Название ссылки')
    link = models.CharField(max_length=256, blank=True, verbose_name='Ссылка')

    def state(self):
        go = self.orders.filter(pay_status=False).count()
        buy = self.orders.filter(pay_status=True).count()
        return f'{buy}/{go}'



class Order(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='ID чата с пользователем')
    link = models.ForeignKey('Link', related_name='orders', on_delete=models.CASCADE, verbose_name='Ссылка, по которой пришел')
    pay_status = models.BooleanField(default=False, verbose_name='Оплатил ли товар')
    end_subscribe = models.DateField(blank=True, null=True, verbose_name='Дата окончания подписки')



