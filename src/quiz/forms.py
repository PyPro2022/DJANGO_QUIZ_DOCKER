# .../DJANGO_QUIZ/quiz/forms.py

from django import forms
from django.core.exceptions import ValidationError

from .models import Choice


class QuestionInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if not (self.instance.QUESTION_MIN_LIMIT <= len(self.forms) <= self.instance.QUESTION_MAX_LIMIT):
            raise ValidationError(
                f'Кол-во вопросов должно быть в диапазоне '
                f'от {self.instance.QUESTION_MIN_LIMIT} '
                f'до {self.instance.QUESTION_MAX_LIMIT}'
            )

        # Валидация на порядок.
        lst_order_num = []
        for form in self.forms:
            lst_order_num.append(form.cleaned_data['order_num']) # получили список значений order_num

        chk_lst = [i for i in range(1, len(lst_order_num)+1)]  # создали контрольный список

        for i in range(len(lst_order_num)):  # сверяем списки по-элементно, чтобы выловить параметры
            if lst_order_num[i] == chk_lst[i]:
                pass
            else:
                raise ValidationError(
                                    f'Вопросы идут не по порядку!'
                                    f'\nORDER NUM должен начинаться с 1\n'
                                    f'и увеличиваться на 1 от вопроса к вопросу.\n'
                                    f"\nОшибка в: <<{self.forms[i].cleaned_data['text']}>>. \n"
                                    f"\n Неверный ORDER_NUM: <<{self.forms[i].cleaned_data['order_num']}>>.\n"

                                    )
        # Валидация на порядок: упрощённый вариант
        # if not chk_lst == lst_order_num:  # выполняем проверку
        #     raise ValidationError(
        #         f'Вопросы идут не по порядку!'
        #         f'\nORDER NUM должен начинаться с 1\n'
        #         f'и увеличиваться на 1 от вопроса к вопросу'
        #     )

        # Валидация на макс. значение. Особо не нужна, т.к. делается автоматом в валидаторе количества вопросов.
        if max(lst_order_num) > self.instance.QUESTION_MAX_LIMIT:
            raise ValidationError(
                f'\nORDER NUM не может быть больше {self.instance.QUESTION_MAX_LIMIT}'
            )


class ChoiceInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        num_correct_answers = sum(form.cleaned_data['is_correct'] for form in self.forms)
        if num_correct_answers == 0:
            raise ValidationError('Необходимо выбрать как минимум 1 вариант.')

        if num_correct_answers == len(self.forms):
            raise ValidationError('НЕ разрешено выбирать все варианты')


class ChoiceForm(forms.ModelForm):
    is_selected = forms.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ['text']


ChoicesFormSet = forms.modelformset_factory(
    model=Choice,
    form=ChoiceForm,
    extra=0
)


#  Кладовка

# for form in self.forms:
#     print(form.cleaned_data['text'], form.cleaned_data['order_num'])

# print(self.forms)
# print(self.forms[0].cleaned_data)
# print(len(self.forms))
# print(lst_order_num)
# print(chk_lst)
# print(chk_lst==lst_order_num)
# print(max(lst_order_num))


# class ChoiceInlineFormSet(forms.BaseInlineFormSet):
#     def clean(self):
#         # lst = []
#         # for form in self.forms:
#         #     if form.cleaned_data['is_correct']:
#         #         lst.append(1)
#         #     else:
#         #         lst.append(0)
#
#         num_correct_answers = sum(form.cleaned_data['is_correct'] for form in self.forms)
#         # num_correct_answers = sum(lst)
#
#         # num_correct_answers = sum(1 for form in self.forms if form.cleaned_data['is_correct'])
#
#         if num_correct_answers == 0:
#             raise ValidationError('Необходимо выбрать как минимум 1 вариант.')
#
#         if num_correct_answers == len(self.forms):
#             raise ValidationError('НЕ разрешено выбирать все варианты')
