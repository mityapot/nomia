from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Choice(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self): 
        return self.text


class Question(models.Model):
    TYPE = {
        0: "Custom",
        1: "Single",
        2: "Multiple"
    }
    text = models.CharField(max_length=800)
    choice_type = models.PositiveIntegerField(choices=TYPE, default=0)
    choices = models.ManyToManyField(
        Choice, related_name='related_polls', blank=True)

    def __str__(self):
        return self.text


class Node(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    # limit = models.Q(app_label='polls', model='Question') | models.Q(app_label='polls', model='Choice')
    node_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    node_object = GenericForeignKey("node_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["node_type", "object_id"]),
        ]

    # def __str__(self):
    #     return f'{self.node_object.__name__}: {self.node_object.text}'


class Poll(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    first_node = models.ForeignKey(Node, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)