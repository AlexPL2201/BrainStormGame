from django.shortcuts import render
from django.views.generic import TemplateView
from questions.models import Question


class QuestionView(TemplateView):
    template_name = 'questions/qes_list.html'

class AddQuestionsView(TemplateView):
    template_name = 'questions/add_quest.html'
