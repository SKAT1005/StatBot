from django.contrib.auth.models import AbstractUser
from django.db import models


class Manager(AbstractUser):
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0)
    bots = models.ManyToManyField()



class Bots(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название бота')

