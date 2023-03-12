from django.urls import path
import questions.views as questions

app_name = 'questions'

urlpatterns = [
    path('', questions.index, name='index'),
]
