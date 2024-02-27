from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.core.exceptions import BadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import *
import logging

logger = logging.getLogger("polls")


class PollsListView(LoginRequiredMixin, ListView):
    paginate_by = 5
    model = Poll
    done = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        done = request.GET.get('done')
        self.done = False if done == "0" or done is None else True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["done"] = self.done
        return context

    def get_queryset(self):
        if self.done:
            return Poll.objects.filter(
                id__in=PollResult.objects.filter(user=self.request.user).values_list('poll', flat=True))
        else:
            return Poll.objects.filter(visibility=True).exclude(
                id__in=PollResult.objects.filter(user=self.request.user).values_list('poll', flat=True))


@login_required()
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id, visibility=True)
    if request.method == 'GET':
        prev_question_id = request.GET.get('question')
        invalid = request.GET.get('invalid')
        if invalid is not None:
            messages.error(request, "Please vote again")
            logger.debug(f'Invalid vote')
        if prev_question_id is None:
            questions = Question.objects.filter(poll_id=poll_id, default=True)[:1]
            current_question = questions[0]
            logger.debug(f'Show first question_{current_question.id}')
        else:
            prev_question_id = int(prev_question_id)
            questions = Question.objects.filter(poll_id=poll_id, pk__gt=prev_question_id)
            if len(questions) == 0:
                logger.debug('Finish vote. No more questions')
                return redirect(f"/polls/result/{poll_id}")
            result = get_object_or_404(PollResult, poll_id=poll_id, user=request.user)
            answers = Answer.objects.filter(poll_result=result)
            current_question = None
            for question in questions:
                conditions = Condition.objects.filter(choice__in=answers.values_list('choice', flat=True),
                                                      question=question)
                if len(conditions) == 0:  # Условий не нашли, поведение по умолчанию
                    if question.default:
                        current_question = question
                        logger.debug(f'Show question_{question.id}. Used default behavior')
                        break
                    else:
                        logger.debug(f'Hide question_{question.id}. Used default behavior')
                        continue
                if len(conditions) == 1:  # Условие единственное, выбираем его
                    if conditions[0].condition_type:
                        current_question = question
                        logger.debug(f'Show question_{question.id}. Used only one condition_{conditions[0].id}')
                        break
                    else:
                        logger.debug(f'Hide question_{question.id}. Used only one condition_{conditions[0].id}')
                        continue
                if len(conditions) > 1:  # Условий несколько, при этом случае отдаем приотет условию "скрыть"
                    hide = None
                    for condition in conditions:
                        if condition.condition_type:
                            continue
                        else:
                            hide = True
                            break
                    if hide:
                        logger.debug(f'Hide question_{question.id}. Chose from multiple condition_{conditions[0].id}')
                        continue
                    else:
                        current_question = question
                        logger.debug(f'Show question_{question.id}. Chose from multiple condition_{conditions[0].id}')
                        break
            if current_question is None:  # Не нашли подходящего вопроса для показа, завершаем опрос
                logger.debug('Finish vote. No questions to show.')
                return redirect(f"/polls/result/{poll_id}")
        context = {"question": current_question}
        return render(request, "polls/vote.html", context)
    elif request.method == 'POST':
        question_id = request.POST.get('question')
        if question_id is None:
            raise BadRequest("No question was provided.")
        question_id = int(question_id)
        question = get_object_or_404(Question, pk=question_id)
        redirect_url = f"/polls/vote/{poll_id}?question={question_id}"
        choices_ids = []
        for key, value in request.POST.items():
            if key.startswith('checkbox_') or key == 'radio':
                choices_ids.append(int(value))
        if len(choices_ids) == 0:
            logger.debug('No choices were selected.')
            return redirect(redirect_url + "&invalid=1")  # Bad vote
        choices = Choice.objects.filter(id__in=choices_ids)
        if len(choices) == 0 or not question.all_belong(choices):
            logger.error('Not all choices from current question.')
            return redirect(redirect_url + "&invalid=1")
        result, created = PollResult.objects.get_or_create(poll_id=poll_id, user=request.user)
        for choice in choices:
            answer = Answer(poll_result=result, choice=choice)
            try:
                answer.full_clean()
            except ValidationError as e:
                logger.error(
                    f"Bad answer. Error: pollresult_{result.id}, choice_{choice.id}, message: {' '.join(e.messages)}")
                continue
            else:
                answer.save()
        return redirect(redirect_url)


@login_required()
def result_poll(request, poll_id):
    result = get_object_or_404(PollResult, poll_id=poll_id, user=request.user)
    answers = Answer.objects.filter(poll_result=result)
    context = {"poll_name": result.poll.name, "answers": answers}
    return render(request, "polls/poll_result.html", context)
