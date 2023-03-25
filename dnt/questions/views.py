from django.shortcuts import render
from django.views.generic import TemplateView
from questions.models import Question


class QuestionView(TemplateView):
    template_name = 'questions/qes_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = Question.objects.all()
        return context_data


class AddQuestionsView(TemplateView):
    template_name = 'questions/add_quest.html'
