from django.contrib import admin
from .models import Question, Category, Type, SubType, Answer


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SubTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(SubType, SubTypeAdmin)
admin.site.register(Answer, AnswerAdmin)