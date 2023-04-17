from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from games.models import Lobby, Game
from questions.models import Question

NULLABLE = {"blank": True, "null": True}


class AuthUser(AbstractUser):

    RANKS = (
        ('iron', 'Железо'),
        ('bronze', 'Бронза'),
        ('silver', 'Серебро'),
        ('gold', 'Золото'),
        ('platinum', 'Платина'),
        ('diamond', 'Алмаз'),
        ('master', 'Мастер'),
        ('grandmaster', 'Грандмастер'),
        ('challenger', 'Претендент')
    )

    nickname = models.CharField(max_length=16, verbose_name='Ник')
    telegram_id = models.PositiveIntegerField(verbose_name='ID Телеграм', **NULLABLE)
    email = models.EmailField(verbose_name='email', **NULLABLE)
    birthdate = models.DateField(verbose_name='Дата рождения', null=True)
    is_moderator = models.BooleanField(default=False, verbose_name='Модератор')
    level = models.PositiveSmallIntegerField(default=1, verbose_name='Уровень')
    current_experience = models.PositiveSmallIntegerField(default=0, verbose_name='Опыт текущего уровня')
    rank = models.CharField(choices=RANKS, default=RANKS[0], max_length=16, verbose_name='Ранг')
    division = models.PositiveSmallIntegerField(default=4, verbose_name='Дивизион', validators=[
            MaxValueValidator(4),
            MinValueValidator(1)
        ])
    current_lp = models.PositiveSmallIntegerField(default=0, verbose_name='Текущие ранговые очки')
    friends = models.ManyToManyField('self', verbose_name='Друзья')
    current_lobby = models.ForeignKey(Lobby, related_name='players', on_delete=models.SET_NULL, **NULLABLE)
    is_lobby_leader = models.BooleanField(default=False)
    current_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    avatar = models.ImageField(upload_to="users", verbose_name=_("Аватар"), **NULLABLE)

    @property
    def get_friends(self):
        return AuthUser.objects.filter(pk__in=self.friends.values_list('pk'))


class QuestionRatedByUser(models.Model):
    """
    Модель для связи вопроса с пользователем.
    Каждая запись - факт оценки вопроса пользователем.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        unique_together = ('question', 'user',)


class Remark(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.CharField(max_length=128, verbose_name='Замечание')
    author = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    rating = models.IntegerField(default=0, verbose_name='Очки')

    class Meta:
        unique_together = ('question', 'author',)

    def __str__(self):
        return f'#{self.text} {self.rating}'