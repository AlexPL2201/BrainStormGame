from django.urls import path
from questions import views

app_name = 'questions'

urlpatterns = [
    path('quest_list/', views.QuestionView.as_view(), name='quest_list'),
    path('quest_list/add_quest/', views.AddQuestionsView.as_view(), name='add_quest'),
]
