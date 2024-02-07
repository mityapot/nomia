from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Poll(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    TYPE = {
        0: "Custom",  # Убрать или оставить ответ с текстовым полем без выбора, боюсь запутаться
        1: "Single",
        2: "Multiple"
    }
    text = models.CharField(max_length=800)
    choice_type = models.PositiveIntegerField(choices=TYPE, default=0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    hierarchy_level = models.PositiveIntegerField(default=0)  # Таким образом задаем порядов вопросов в опросе или избыточно ?

    def __str__(self):
        return self.text


class Choice(models.Model):
    text = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self): 
        return self.text


class Condition(models.Model):
    TYPE = {
        0: "Default show",
        1: "Default hide",  # Не избыточно ли default hide?
        2: "Hide",
        3: "Show",
    }
    condition_type = models.PositiveIntegerField(choices=TYPE, default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)


class PollResults(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Answer(models.Model):
    poll_result = models.ForeignKey(PollResults, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)




