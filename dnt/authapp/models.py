from django.db import models
from django.contrib.auth.models import AbstractUser
from games.models import Lobby, Game


class AuthUser(AbstractUser):

    nickname = models.CharField(max_length=16, verbose_name='Ник')
    telegram_id = models.PositiveIntegerField(verbose_name='ID Телеграм', null=True, blank=True)
    email = models.EmailField(verbose_name='email', null=True, blank=True)
    birthdate = models.DateField(verbose_name='Дата рождения', null=True)
    is_moderator = models.BooleanField(default=False, verbose_name='Модератор')
    level = models.PositiveSmallIntegerField(default=1, verbose_name='Уровень')
    current_experience = models.PositiveSmallIntegerField(default=0, verbose_name='Опыт текущего уровня')
    friends = models.ManyToManyField('self', verbose_name='Друзья')
    current_lobby = models.ForeignKey(Lobby, related_name='players', on_delete=models.SET_NULL, null=True, blank=True)
    current_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)



