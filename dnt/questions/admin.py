from django.contrib import admin
from questions.models import Question, Category, Type, SubType, Answer, QuestionComplaint, Remark

# # admin.site.register(Question)
# admin.site.register(Category)
# admin.site.register(Type)
# admin.site.register(SubType)
# admin.site.register(Answer)
# admin.site.register(QuestionComplaint)
# admin.site.register(Remark)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category', 'question', 'answer', 'is_validated')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

@admin.register(SubType)
class SubTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'type')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'answer', 'subtype')

@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'text')

@admin.register(QuestionComplaint)
class QuestionComplaintAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'text')