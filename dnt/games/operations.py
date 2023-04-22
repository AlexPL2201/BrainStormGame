import os
import django
from django.db.models import Q
from typing import List

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
django.setup()

from authapp.models import AuthUser, QuestionRatedByUser, Remark
from questions.models import Question


class GameProcessForUser:
    """
    Класс для операций пользователя в процессе игры
    """

    def __init__(self, user: AuthUser):
        """
        Создание объекта процесса игры.
        Создается для конкретного пользователя
        """
        self.user = user

    def get_next_question(self):
        pass
