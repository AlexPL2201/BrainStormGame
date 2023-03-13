from django.contrib import admin
from .models import AuthUser


class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


admin.site.register(AuthUser, AuthUserAdmin)
