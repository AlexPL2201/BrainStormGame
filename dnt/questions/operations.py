import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnt.settings')
django.setup()

from authapp.models import AuthUser, QuestionRatedByUser, Remark
from questions.models import Question

MIN_LEVEL_TO_RATE_QUESTION = 5


class UserLevelTooLow(Exception):
    pass


class NoUnratedQuestionsForUser(Exception):
    pass


class SettingRatingToQuestionByUser:
    """
    Класс для операций пользователя с вопросами: оценка вопроса, просмотр замечаний, оценка замечаний
    """

    def __init__(self, user: AuthUser):
        """
        Создание объекта процесса оценки.
        Создается для конкретного пользователя
        """
        if user.level >= MIN_LEVEL_TO_RATE_QUESTION:
            self.user = user
            self.current_question = None
        else:
            raise UserLevelTooLow

    def get_next_question(self):
        """
        Метод перехода к следующему вопросу
        """
        already_rated_questions = QuestionRatedByUser.objects.filter(user_id=self.user.pk)

        # TODO написать по-человечески, разобравшись с фильтром ниже:
        # self.current_question = Question.objects.get(pk__not_in=[question.question_id for question in already_rated_questions])

        # А пока так:
        already_rated_questions_pks = [question.question_id for question in already_rated_questions]
        questions = Question.objects.all()
        for question in questions:
            if question.pk not in already_rated_questions_pks:
                self.current_question = question
                break
        else:
            raise NoUnratedQuestionsForUser

    def rate_current_question(self, bad: bool = False):
        """
        Метод для оценки текущего вопроса
        :param bad: Dislike если True, Like
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

    def add_remark_to_current_question(self, text: str):
        """
        Метод для добавления замечания к текущему вопросу
        :param text: Текст замечания
        :return:
        """
        remark = Remark(question=self.current_question,
                        text=text,
                        author=self.user)
        remark.save()

    def get_remarks_for_current_question(self) -> list:
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
        :param bad:  Dislike если True, Like
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
    process.get_next_question()
    print(process.current_question.question)
    # process.rate_current_question(bad=False)
    # process.add_remark_to_current_question(text='Вообще тлен')
    for remark in process.get_remarks_for_current_question():
        print(remark.text)
    # remark = process.get_remarks_for_current_question()[0]
    # process.rate_remark(remark=remark, bad=True)
