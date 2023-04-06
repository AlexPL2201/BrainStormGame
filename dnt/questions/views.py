from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, DeleteView, UpdateView, CreateView, DetailView

from authapp.models import Remark, AuthUser
from questions.models import Question, Category, Type, SubType, Answer, QuestionComplaint


class QuestionView(TemplateView):
    template_name = 'questions/qes_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = Question.objects.all()
        context_data['complaints'] = QuestionComplaint.objects.filter()
        return context_data

    def post(self, request, *args, **kwargs):
        if all(
                (
                        request.POST.get('question_id'),
                        request.POST.get('complaint'),
                )
        ):
            print(request.POST)
            new_complaint = QuestionComplaint.objects.create(
                question=Question.objects.get(pk=int(request.POST.get('question_id'))),
                text=request.POST.get('complaint')
            )
            new_complaint.save()
            messages.add_message(request, messages.INFO, 'Замечание добавлено')
            return HttpResponseRedirect(reverse('quest:quest'))
        else:
            messages.add_message(
                request, messages.WARNING,
                'Не удалось добавить замечание'
            )
            return HttpResponseRedirect(reverse('quest:quest'))


class QuestionDeleteView(DeleteView):
    model = Question
    success_url = reverse_lazy('quest:quest')


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ('question', 'is_validated')
    success_url = reverse_lazy('quest:quest')


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
                    name=request.POST.get('category')
                )
                new_category.save()
                new_type = Type.objects.create(
                    name=request.POST.get('type')
                )
                new_type.save()
                new_subtype = SubType.objects.create(
                    name=request.POST.get('subtype'),
                    type=Type.objects.get(name=request.POST.get('type'))
                )
                new_subtype.save()
                new_answer = Answer.objects.create(
                    answer=request.POST.get('answer'),
                    subtype=SubType.objects.get(name=request.POST.get('subtype'))
                )
                new_answer.save()
                new_quest = Question.objects.create(
                    category=new_category,
                    question=request.POST.get('question'),
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

class GradeQuestionView(TemplateView):
    template_name = 'questions/grade_quest.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['question_list'] = Question.objects.all()
        return context_data

    def post(self, request, *args, **kwargs):
        try:
            if all(
                    (
                            request.POST.get('question'),
                            request.POST.get('text'),
                            request.POST.get('author'),
                            request.POST.get('rating')
                    )
            ):
                new_remark = Remark.objects.create(
                    question=Question.objects.get(question=request.POST.get('question')),
                    text=request.POST.get('text'),
                    author=AuthUser.objects.get(username=request.POST.get('author')),
                    rating=request.POST.get('rating'),
                )
                new_remark.save()
                messages.add_message(request, messages.INFO, 'Оценка выполнена')
                return HttpResponseRedirect(reverse('quest:grade_quest'))
            else:
                messages.add_message(
                    request, messages.WARNING,
                    'Не удалось выполнить оценку'
                )
                return HttpResponseRedirect(reverse('quest:grade_quest'))
        except Exception as ex:
            messages.add_message(
                request, messages.WARNING,
                'Не удалось выполнить оценку'
            )
            return HttpResponseRedirect(reverse('quest:grade_quest'))

class OfferQuestionView(TemplateView):
    template_name = 'questions/offer_quest.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['type_list'] = Type.objects.all()
        context_data['subtype_list'] = SubType.objects.all()

        return context_data

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
                    name=request.POST.get('category')
                )
                new_category.save()
                new_answer = Answer.objects.create(
                    answer=request.POST.get('answer'),
                    subtype=SubType.objects.get(name=request.POST.get('subtype'))
                )
                new_answer.save()
                new_quest = Question.objects.create(
                    category=new_category,
                    question=request.POST.get('question'),
                    answer=new_answer,
                )
                new_quest.save()
                messages.add_message(request, messages.INFO, 'Вопрос добавлен успешно')
                return HttpResponseRedirect(reverse('quest:offer_quest'))
            else:
                messages.add_message(
                    request, messages.WARNING,
                    'Не удалось добавить вопрос'
                )
                return HttpResponseRedirect(reverse('quest:offer_quest'))
        except Exception as ex:
            messages.add_message(
                request, messages.WARNING,
                'Не удалось добавить вопрос'
            )
            return HttpResponseRedirect(reverse('quest:offer_quest'))
