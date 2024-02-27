from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Poll(models.Model):
    """
    Модель для описания опросов. С помощью visibility управляем будет ли показан опрос у пользователей.
    """
    SHOW = {
        False: "Disable",
        True: "Anable"
    }
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    visibility = models.BooleanField(default=False, choices=SHOW)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.visibility:  # Не позволяем показывать опрос у пользователя, если там ноль вопросов или вопрос с одним вариантом ответа
            return
        questions = Question.objects.filter(poll=self)
        if questions.count() < 1:
            raise ValidationError(f'Poll must have at least one question. Poll: {self.__str__()}.')
        inv_questions = []
        first_question = None
        for question in questions:
            if question.default:
                first_question = True
            if not question.check_choices:
                inv_questions.append(question.id)
        if not first_question:
            raise ValidationError(f'No first question in poll {self.__str__()}')
        if len(inv_questions) != 0:
            raise ValidationError(
                f"Each question in poll must have at least two choices. Poll: {self.__str__()}. Invalid_questions: {', '.join(inv_questions)}")


class Question(models.Model):
    """
    Модель для описания вопросов. Считаем, что вопросы упорядоченными по id, но если надо менять порядок,
    то необходимо добавить поле для упорядочивания. Также считаем, что у нас бывают два типа вопросов:
    один и множественный выбор.
    """
    TYPE = {
        0: "Single",
        1: "Multiple"
    }
    DEFAULT = {
        False: "Hide",
        True: "Show",
    }
    default = models.BooleanField(choices=DEFAULT, default=False)  # Описание поведения по умолчанию
    text = models.CharField(max_length=800)
    choice_type = models.PositiveIntegerField(choices=TYPE, default=0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text

    def belong_all(self, choices):
        """Проверяет все ли choices принадлежат одному question"""
        result_questions = choices.values_list('question', flat=True)
        if len(set(result_questions)) != 1:
            return False
        if self.id != result_questions[0]:
            return False
        return True

    @property
    def check_choices(self):
        """Проверяет больше ли одного choice у question"""
        choices_num = Choice.objects.filter(question=self).count()
        if choices_num <= 1:
            return False
        return True


class Choice(models.Model):
    """
    Модель для описания ответов на вопрос.
    """
    text = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Condition(models.Model):
    """
    Модель для описания алгоритма показа вопросов в зависимости от предыдущих ответов.
    """
    TYPE = {
        False: "Hide",
        True: "Show",
    }
    condition_type = models.BooleanField(choices=TYPE, default=False)  # Показать или скрыть
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['choice', 'question'], name='unique_condition')
        ]

    def clean(self):
        if self.question.poll != self.choice.question.poll:
            raise ValidationError('Question and choice must be from the same poll.')
        if self.choice.question.id >= self.question.id:
            raise ValidationError('Wrong order of questions.')


class PollResult(models.Model):
    """
    Модель описания результатов ответа пользователя на опрос.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['poll', 'user'], name='unique_result')

        ]

    @property
    def ansvered_questions(self):
        """Возвращает вопросы из опроса, на которые ответили"""
        answeres = self.answer_set.all()
        questions = answeres.values_list('choice__question_id', flat=True)
        return Question.objects.filter(id__in=questions)


class Answer(models.Model):
    """
    Модель описания ответа пользователя на вопрос.
    """
    poll_result = models.ForeignKey(PollResult, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def clean(self):
        if self.choice.question not in self.poll_result.poll.question_set.all():
            raise ValidationError('Question is not in this poll.')
        if self.choice.question.choice_type == 0:
            if Answer.objects.filter(poll_result=self.poll_result, choice__question=self.choice.question).exists():
                raise ValidationError('Question with single choice already have answer.')
