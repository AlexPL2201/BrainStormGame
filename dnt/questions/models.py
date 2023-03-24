from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='Категория')


class Type(models.Model):
    name = models.CharField(max_length=64, verbose_name='Тип')


class SubType(models.Model):
    name = models.CharField(max_length=64, verbose_name='Подтип')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='subtypes', verbose_name='Тип')


class Answer(models.Model):
    answer = models.CharField(max_length=64, verbose_name='Ответ')
    subtype = models.ForeignKey(SubType, on_delete=models.CASCADE, verbose_name='Подтип')


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Тема вопроса')
    question = models.CharField(max_length=128, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Правильный ответ')
    is_validated = models.BooleanField(default=False, verbose_name='Одобрен')
    rating = models.IntegerField(default=0, verbose_name='Очки')


class QuestionComplaint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.CharField(max_length=128, verbose_name='Жалоба')
