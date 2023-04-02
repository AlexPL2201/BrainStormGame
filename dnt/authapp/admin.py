from django.contrib import admin
from .models import AuthUser, QuestionRatedByUser


class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'email', 'password', 'birthdate', 'avatar')


class QuestionRatedByUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'question_id')


admin.site.register(AuthUser, AuthUserAdmin)
admin.site.register(QuestionRatedByUser, QuestionRatedByUserAdmin)
