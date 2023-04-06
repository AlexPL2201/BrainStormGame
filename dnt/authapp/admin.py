from django.contrib import admin
from .models import AuthUser, QuestionRatedByUser, Remark


class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'email', 'password', 'birthdate', 'avatar')


class QuestionRatedByUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'question_id')

@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'text')

admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(QuestionRatedByUser, QuestionRatedByUserAdmin)
