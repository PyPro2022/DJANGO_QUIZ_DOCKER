# .../DJANGO_QUIZ/quiz/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin

from .forms import ChoicesFormSet
from .models import Exam, Result, Question


class ExamListView(ListView):
    model = Exam
    template_name = 'exams/list.html'
    context_object_name = 'exams'


class ExamDetailView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = Exam
    template_name = 'exams/details.html'
    context_object_name = 'exam'
    pk_url_kwarg = 'uuid'
    paginate_by = 3

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return self.model.objects.get(uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(object_list=self.get_queryset(), **kwargs)
        return context

    def get_queryset(self):
        return Result.objects.filter(
            exam=self.get_object(),
            user=self.request.user
        ).order_by('state', '-create_timestamp')


class ExamResultCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result = Result.objects.create(
            user=request.user,
            exam=Exam.objects.get(uuid=uuid),
            state=Result.STATE.NEW,
            current_order_number=0
        )

        result.save()

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                }
            )
        )


class ExamResultQuestionView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        result = Result.objects.get(uuid=kwargs.get('res_uuid'))
        question = Question.objects.get(
            exam__uuid=uuid,
            order_num=result.current_order_number + 1
        )

        choices = ChoicesFormSet(queryset=question.choices.all())

        return render(request, 'exams/question.html', context={'question': question, 'choices': choices})

    def post(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        result = Result.objects.get(uuid=res_uuid)
        question = Question.objects.get(
            exam__uuid=uuid,
            order_num=result.current_order_number + 1
        )
        choices = ChoicesFormSet(data=request.POST)
        selected_choices = ['is_selected' in form.changed_data for form in choices.forms]
        # print('>>>>>>>',selected_choices)  # служебная информация для нужд отладки
        if selected_choices.count(True) > 1 or selected_choices.count(True) == 0:
            messages.error(self.request, '[!] Так нельзя! Выберите только один вариант ответа.')
            return HttpResponseRedirect(
                reverse(
                    'quiz:question',
                    kwargs={
                        'uuid': uuid,
                        'res_uuid': res_uuid,
                    }
                )
            )

        result = Result.objects.get(uuid=res_uuid)
        result.update_result(result.current_order_number + 1, question, selected_choices)

        if result.state == Result.STATE.FINISHED:
            return HttpResponseRedirect(
                reverse(
                    'quiz:result_details',
                    kwargs={
                        'uuid': uuid,
                        'res_uuid': result.uuid
                    }
                )
            )

        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': res_uuid,
                }
            )
        )


class ExamResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'results/details.html'
    context_object_name = 'result'
    pk_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('res_uuid')
        return self.get_queryset().get(uuid=uuid)

    def get_context_data(self, **kwargs): # служебная информация для нужд отладки
        x = super().get_context_data()
        # print(x)
        return x


class ExamResultUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        res_uuid = kwargs.get('res_uuid')
        user = request.user

        result = Result.objects.get(
            user=user,
            uuid=res_uuid,
            exam__uuid=uuid,
        )
        return HttpResponseRedirect(
            reverse(
                'quiz:question',
                kwargs={
                    'uuid': uuid,
                    'res_uuid': result.uuid,
                }
            )
        )


class ExamResultDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Result
    context_object_name = 'result'
    template_name = 'exams/delete.html'
    permission_required = ['accounts.view_statistics']

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('res_uuid')
        return self.get_queryset().get(uuid=uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = Exam.objects.get(
            results=self.get_object(),
        )
        return context

    def get_success_url(self):
        uuid = self.get_context_data()['result'].exam.uuid
        return reverse('quiz:details', kwargs={'uuid': uuid})

