from django.db.models import base
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('polls', views.PollViewSet, basename='poll')
router.register('question', views.QuestionViewSet, basename='question')
router.register('choice', views.ChoiceViewSet, basename='choice')

urlpatterns = [
    path('polls/active/', views.ActivePolls.as_view()),
    path('polls/<int:pk>/pass/', views.PassedPollCreateView.as_view()),
    path('polls/passed/', views.PassedPollListView.as_view()),
    path('polls/passed/<int:pk>/', views.PassedPollDetailView.as_view()),
] + router.urls
