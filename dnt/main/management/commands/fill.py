import json
from django.conf import settings
from django.core.management.base import BaseCommand
from authapp.models import AuthUser
from questions.models import Question, Answer, Type, SubType, Category


def load_from_json(file_name):
    with open(f'{settings.BASE_DIR}/json/{file_name}.json', 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


class Command(BaseCommand):

    def handle(self, *args, **options):
        categories = load_from_json('categories')
        types = load_from_json('types')
        subtypes = load_from_json('subtypes')
        answers = load_from_json('answers')
        questions = load_from_json('questions')

        Category.objects.all().delete()
        for category in categories:
            Category.objects.create(**category)

        Type.objects.all().delete()
        for type_ in types:
            Type.objects.create(**type_)

        SubType.objects.all().delete()
        for subtype in subtypes:
            subtype['type'] = Type.objects.get(name=subtype['type'])
            SubType.objects.create(**subtype)

        Answer.objects.all().delete()
        for answer in answers:
            answer['subtype'] = SubType.objects.get(name=answer['subtype'])
            Answer.objects.create(**answer)

        Question.objects.all().delete()
        for question in questions:
            question['category'] = Category.objects.get(name=question['category'])
            question['answer'] = Answer.objects.get(answer=question['answer'])
            Question.objects.create(**question)

        AuthUser.objects.all().delete()

        AuthUser.objects.create_superuser(username='pepper', password='pepper123', nickname='pepper',
                                          birthdate='2019-01-01', is_moderator=True)

        for i in range(2, 10):
            AuthUser.objects.create_superuser(username=f'pepper{i}', password='pepper123', nickname=f'pepper{i}',
                                              birthdate='2019-01-01')

        pepper = AuthUser.objects.get(username='pepper')
        pepper2 = AuthUser.objects.get(username='pepper2')
        pepper.friends.add(pepper2)
        pepper2.friends.add(pepper)
