from django.urls import path
from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.QuestionView.as_view(), name='quest'),
    path('add_quest/', views.AddQuestionsView.as_view(), name='add_quest'),
    path('<int:pk>/delete_quest/', views.QuestionDeleteView.as_view(), name='delete_quest'),
    path('<int:pk>/update_quest/', views.QuestionUpdateView.as_view(), name='update_quest'),
    path('grade_quest/', views.GradeQuestionView.as_view(), name='grade_quest'),
    path('offer_quest/', views.OfferQuestionView.as_view(), name='offer_quest'),
]
