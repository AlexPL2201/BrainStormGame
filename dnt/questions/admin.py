from django.contrib import admin
from .models import Question, Category, Type, SubType, Answer, QuestionComplaint

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'category', 'created_at', 'is_validated')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SubType)
class SubTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer', 'subtype')

@admin.register(QuestionComplaint)
class QuestionComplaintAdmin(admin.ModelAdmin):
    list_display = ('question', 'text')

