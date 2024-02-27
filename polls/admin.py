from django.contrib import admin, messages
from .models import Choice, Poll, Question, Condition, PollResult
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'visibility']
    actions = ["make_visible"]

    @admin.action(description="Mark selected polls as visible")
    def make_visible(self, request, queryset):
        try:
            for poll in queryset:
                poll.visibility = True
                poll.full_clean()
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
        else:
            queryset.update(visibility=True)


class ChoiceInline(admin.TabularInline):
    model = Choice


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'choice_type', 'poll', 'default']
    inlines = [
        ChoiceInline,
    ]


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ['condition_type', 'question', 'choice']
