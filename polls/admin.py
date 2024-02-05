from django.contrib import admin
from .models import Choice, Poll, Question, Node


admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Poll)
admin.site.register(Node)