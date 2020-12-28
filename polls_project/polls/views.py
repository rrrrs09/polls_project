from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import Poll, PassedPoll, Question, Choice
from .permissions import IsAdmin, IsUser
from . import serializers


class ActivePolls(generics.ListAPIView):
    """Возвращает список активных опросов"""
    permission_classes = [AllowAny]
    serializer_class = serializers.PollSerializer
    queryset = Poll.objects.filter(stopped_at=None)


class PollViewSet(viewsets.ModelViewSet):
    """Представление для работы с опросами администратора"""
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post', 'put', 'delete']

    @action(methods=['post'], detail=True)
    def stop(self, request, pk):
        """Завершает опрос"""
        poll = self.get_object()
        if poll.stopped_at is not None:
            msg = {'detail': 'Опрос уже завершён'}
            return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

        poll.stopped_at = timezone.now()
        poll.save()

        serializer = self.get_serializer(poll)
        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        return Poll.objects.filter(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.PollDetailSerializer
        return serializers.PollSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """Представление для работы с вопросами администратора"""
    permission_classes = [IsAdmin]
    http_method_names = ['post', 'put', 'delete']

    def get_queryset(self):
        return Question.objects.filter(poll__author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.QuestionCreateSerializer
        return serializers.QuestionUpdateSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    """Представление для работы с вариантами ответов администратора"""
    permission_classes = [IsAdmin]
    http_method_names = ['post', 'put', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        question = instance.question
        if (question.question_type != Question.TEXT_CHOICE and
                question.choices.count() == 1):
            msg = 'У вопроса с выбором ответа должен быть хотя бы один вариант.'
            return Response(data={'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Choice.objects.filter(question__poll__author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ChoiceCreateSerializer
        return serializers.ChoiceSerializer


class PassedPollCreateView(generics.CreateAPIView):
    """Представления для прохождения опроса"""
    permission_classes = [AllowAny]
    serializer_class = serializers.AnswerSerializer
    queryset = Poll.objects.filter(stopped_at=None)

    def create(self, request, *args, **kwargs):
        user = request.user
        print(user)
        if not user.is_anonymous:
            if user.groups.filter(name='admins').exists():
                raise PermissionDenied()

        poll = self.get_object()
        serializer = self.serializer_class(data=request.data, many=True, context={'poll': poll})
        serializer.is_valid(raise_exception=True)

        validated_questions = set(map(lambda x: x['question'], serializer.validated_data))
        if len(validated_questions) != poll.questions.count():
            msg = 'Все вопросы являются обязательными.'
            return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

        if user.is_anonymous:
            passed_poll = PassedPoll.objects.create(poll=poll)
        else:
            passed_poll = PassedPoll.objects.create(user=user, poll=poll)
        serializer.save(passed_poll=passed_poll)

        return Response(serializer.data)


class PassedPollListView(generics.ListAPIView):
    """Возвращает список пройденных пользователем опросов"""
    serializer_class = serializers.PassedPollListSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        queryset = PassedPoll.objects.filter(user=self.request.user) \
            .select_related('poll').values(
                'id', 'passed_at', title=F('poll__title'),
                description=F('poll__description'),
            )
        return queryset


class PassedPollDetailView(generics.RetrieveAPIView):
    """
    Возвращает детализированное представление пройденного
    пользователем опроса с ответами
    """
    serializer_class = serializers.PassedPollDetailSerializer
    permission_classes = [IsUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, context={'passed_poll': instance})
        return Response(serializer.data)

    def get_queryset(self):
        return PassedPoll.objects.filter(user=self.request.user)
