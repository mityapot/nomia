from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.PollsListView.as_view(), name='list'),
    path('vote/<int:poll_id>', views.vote, name='vote'),
    path('result/<int:poll_id>', views.result_poll, name='result'),
]