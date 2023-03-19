import os
import django
from typing import List

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
django.setup()

from authapp.models import AuthUser, QuestionRatedByUser, Remark
from questions.models import Question

MIN_LEVEL_TO_RATE_QUESTION = 5


class UserLevelTooLow(Exception):
    pass


class NoUnratedQuestionsForUser(Exception):
    pass


class AlreadyRemarkedByThisUser(Exception):
    pass


class SettingRatingToQuestionByUser:
    """
    Класс для операций пользователя с вопросами: оценка вопроса, просмотр замечаний, оценка замечаний

    TODO Что еще нужно доделать ближе к релизу:
    - не давать пользователю оценивать вопросы, заведенные им (допилить модель вопроса и логику)
    - не давать пользователю оценивать замечания, заведенные им.
    """

    def __init__(self, user: AuthUser):
        """
        Создание объекта процесса оценки.
        Создается для конкретного пользователя
        """
        if user.level >= MIN_LEVEL_TO_RATE_QUESTION:
            self.user = user
            self.current_question = None
            self.get_next_question()
        else:
            raise UserLevelTooLow

    def get_next_question(self):
        """
        Метод перехода к следующему вопросу
        """
        already_rated_questions = QuestionRatedByUser.objects.filter(user_id=self.user.pk)
        not_yet_rated_questions = Question.objects.exclude(
            pk__in=[question.question_id for question in already_rated_questions])
        if not_yet_rated_questions:
            self.current_question = not_yet_rated_questions[0]
        else:
            self.current_question = None
            raise NoUnratedQuestionsForUser

    def rate_current_question(self, bad: bool = False):
        """
        Метод для оценки текущего вопроса
        :param bad: Dislike если True, Like если False (по умолчанию)
        :return:
        """
        if not bad:
            self.current_question.rating += 1
        else:
            self.current_question.rating -= 1
        self.current_question.save()
        question_rated_by_user = QuestionRatedByUser(question=self.current_question,
                                                     user=self.user)
        question_rated_by_user.save()

    def ability_to_remark_question(self):
        try:
            Remark.objects.get(question_id=self.current_question.pk,
                               author_id=self.user.pk)
            return False
        except Remark.DoesNotExist:
            return True

    def add_remark_to_current_question(self, text: str):
        """
        Метод для добавления замечания к текущему вопросу
        :param text: Текст замечания
        :return:
        """
        if self.ability_to_remark_question():
            remark = Remark(question=self.current_question,
                            text=text,
                            author=self.user)
            remark.save()
        else:
            raise AlreadyRemarkedByThisUser

    def get_remarks_for_current_question(self) -> List[Remark]:
        """
        Метод получения объектов замечаний к текущему вопросу
        :return:
        """
        return Remark.objects.filter(question=self.current_question)

    @staticmethod
    def rate_remark(remark: Remark, bad: bool = False):
        """
        Метод оценки замечания
        :param remark: Объект замечания
        :param bad:  Dislike если True, Like если False (по умолчанию)
        :return:
        """
        if not bad:
            remark.rating += 1
        else:
            remark.rating -= 1
        remark.save()


if __name__ == '__main__':
    # Тестирование
    user = AuthUser.objects.get(username='taraskvitko')
    process = SettingRatingToQuestionByUser(user)
    # process.get_next_question()
    print(process.current_question.question)
    # process.rate_current_question(bad=False)
    # process.add_remark_to_current_question(text='Вообще тлен')
    # for remark in process.get_remarks_for_current_question():
    #     print(remark.text)
    # remark = process.get_remarks_for_current_question()[0]
    # print(remark.text)
    # process.rate_remark(remark=remark, bad=True)
