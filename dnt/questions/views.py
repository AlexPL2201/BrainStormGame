from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from questions.models import Question, Category, Type, SubType, Answer


class QuestionView(TemplateView):
    template_name = 'questions/qes_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = Question.objects.all()
        return context_data


class AddQuestionsView(TemplateView):
    template_name = 'questions/add_quest.html'

    def post(self, request, *args, **kwargs):
        try:
            if all(
                    (
                        request.POST.get('question'),
                        request.POST.get('category'),
                        request.POST.get('type'),
                        request.POST.get('subtype'),
                        request.POST.get('answer'),
                    )
            ):
                new_category = Category.objects.create(
                    name = request.POST.get('category')
                )
                new_category.save()
                new_type = Type.objects.create(
                    name = request.POST.get('type')
                )
                new_type.save()
                new_subtype = SubType.objects.create(
                    name = request.POST.get('subtype'),
                    type = new_type
                )
                new_subtype.save()
                new_answer = Answer.objects.create(
                    answer = request.POST.get('answer'),
                    subtype = new_subtype
                )
                new_answer.save()
                new_quest = Question.objects.create(
                    category=new_category,
                    question = request.POST.get('question'),
                    answer=new_answer,
                )
                new_quest.save()
                messages.add_message(request, messages.INFO, 'Вопрос добавлен успешно')
                return HttpResponseRedirect(reverse('quest:add_quest'))
            else:
                messages.add_message(
                    request, messages.WARNING,
                    'Не удалось добавить вопрос'
                )
                return HttpResponseRedirect(reverse('quest:add_quest'))
        except Exception as ex:
            messages.add_message(
                request, messages.WARNING,
                'Не удалось добавить вопрос'
            )
            return HttpResponseRedirect(reverse('quest:add_quest'))
