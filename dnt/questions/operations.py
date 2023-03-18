from authapp.models import AuthUser
from questions.models import Question


MIN_LEVEL_TO_RATE_QUESTION = 5


class UserLevelTooLow(Exception):
    pass


class SettingRatingToQuestionByUser:
    def __init__(self, user: AuthUser):
        if AuthUser.level >= MIN_LEVEL_TO_RATE_QUESTION:
            self.user = user
        else:
            raise UserLevelTooLow

    def _get_next_question_to_rate(self):
        question = Question.objects.first()
