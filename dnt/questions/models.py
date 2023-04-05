from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='Категория')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'#{self.name}'


class Type(models.Model):
    name = models.CharField(max_length=64, verbose_name='Тип')

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return f'#{self.name}'


class SubType(models.Model):
    name = models.CharField(max_length=64, verbose_name='Подтип')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='subtypes', verbose_name='Тип')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'#{self.name}'


class Answer(models.Model):
    answer = models.CharField(max_length=64, verbose_name='Ответ')
    subtype = models.ForeignKey(SubType, on_delete=models.CASCADE, verbose_name='Подтип')

    def __str__(self):
        return f'#{self.answer}'


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Тема вопроса')
    question = models.CharField(max_length=128, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Правильный ответ')
    is_validated = models.BooleanField(default=False, verbose_name='Одобрен')
    rating = models.IntegerField(default=0, verbose_name='Очки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'#{self.question}'


class QuestionComplaint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.CharField(max_length=128, verbose_name='Жалоба')

    def __str__(self):
        return f'#{self.text}'