from django.urls import path
from .views import *

urlpatterns = [
    path('', login_register, name='login_register'),
    path('logout/', logout_view, name='logout'),
    path('bot_list/', bot_list, name='bot_list'),
    path('create_bot/', create_bot, name='create_bot'),
    path('create_link/<int:pk>/', create_link, name='create_link'),
    path('bot/<int:pk>/', bot_detail, name='bot_detail'),
    path('webhook/', webhook_view, name='webhook'), # /my_app/webhook/
]