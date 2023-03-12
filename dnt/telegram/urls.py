from django.urls import path
import telegram.views as telegram

app_name = 'telegram'

urlpatterns = [
    path('', telegram.index, name='index'),
]
