from rest_framework import serializers

from .models import Poll, Question, Choice, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка и изменения вариантов ответа"""
    class Meta:
        model = Choice
        exclude = ['question']


class ChoiceCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вариантов ответа"""
    class Meta:
        model = Choice
        fields = '__all__'

    def validate_question(self, question):
        user = self.context['request'].user
        if question.poll.author != user:
            msg = 'Некорректный идентификатор вопроса.'
            raise serializers.ValidationError(msg)
        if question.question_type == Question.TEXT_CHOICE:
            msg = 'У текстового вопроса не может быть вариантов ответа.'
            raise serializers.ValidationError(msg)
        return question


class QuestionListSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка вопросов"""
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'choices']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вопросов"""
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'poll', 'text', 'question_type', 'choices']

    def create(self, validated_data):
        choices = None
        if validated_data.get('choices'):
            choices = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        if choices:
            for choice_data in choices:
                Choice.objects.create(question=question, **choice_data)
        return question

    def validate_poll(self, poll):
        user = self.context['request'].user
        if poll.author == user:
            return poll
        msg = 'Некорректный идентификатор опроса.'
        raise serializers.ValidationError(msg)

    def validate(self, data):
        choices = data.get('choices')
        if data['question_type'] == Question.TEXT_CHOICE:
            if choices is not None:
                msg = 'У текстового вопроса не может быть вариантов ответа.'
                raise serializers.ValidationError(msg)
        else:
            if not choices:
                msg = 'У вопроса с выбором ответа должен быть хотя бы один вариант.'
                raise serializers.ValidationError(msg)
        return data


class QuestionUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения вопросов"""
    class Meta:
        model = Question
        fields = ['id', 'text']


class PollSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка, создания и изменения опросов"""
    started_at = serializers.DateTimeField(read_only=True)
    stopped_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'started_at', 'stopped_at']


class PollDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детализированного представления опросов"""
    started_at = serializers.DateTimeField(read_only=True)
    stopped_at = serializers.DateTimeField(read_only=True)
    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'started_at',
                  'stopped_at', 'questions']


class AnswerSerializer(serializers.ModelSerializer):
    """Сериализатор ответа на вопрос"""
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'choices']
        extra_kwargs = {'choices': {'required': False}}

    def validate(self, data):
        error = None
        question = data['question']
        if question.poll != self.context['poll']:
            error = 'Такого вопроса нет.'
            raise serializers.ValidationError(error)

        if question.question_type == Question.TEXT_CHOICE:
            if not data.get('text'):
                error = 'Требуется текстовый ответ.'
                raise serializers.ValidationError(error)
            if data.get('choices'):
                error = 'У текстового вопроса не может быть вариантов ответа.'
                raise serializers.ValidationError(error)
        else:
            if data.get('text'):
                error = 'У вопросов с выбором вариантов не может быть текстового ответа.'
                raise serializers.ValidationError(error)

            user_choices = data.get('choices')
            if not user_choices:
                error = 'Требуется вариант ответа.'
                raise serializers.ValidationError(error)

            if (question.question_type == Question.SINGLE_CHOICE and
                    len(user_choices) > 1):
                error = 'Требуется один вариант.'
                raise serializers.ValidationError(error)

            question_choices = question.choices.all()
            for choice in user_choices:
                if choice not in question_choices:
                    error = 'Такого варианта нет.'
                    raise serializers.ValidationError(error)
        return data


class PassedPollListSerializer(serializers.Serializer):
    """Сериализатор для вывода списка пройденных пользователем опросов"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    passed_at = serializers.DateTimeField()


class SelectedChoiceSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка вариантов ответа

    Поле selected имеет тип булево и показывает был ли выбран вариант
    """
    selected = serializers.SerializerMethodField()

    def get_selected(self, choice):
        passed_poll = self.context['passed_poll']
        return passed_poll.answers.filter(choices__pk=choice.pk).exists()

    class Meta:
        model = Choice
        exclude = ['question']


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка вопросов с ответами"""
    choices = SelectedChoiceSerializer(many=True)
    answer = serializers.SerializerMethodField()

    def get_answer(self, question):
        if question.question_type == Question.TEXT_CHOICE:
            return Answer.objects.filter(
                passed_poll=self.context['passed_poll'],
                question=question
            ).first().text
        return None

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'answer', 'choices']


class PassedPollDetailSerializer(serializers.Serializer):
    """Сериализатор для детализированного представления пройденного опроса"""
    id = serializers.IntegerField()
    title = serializers.CharField(source='poll.title')
    description = serializers.CharField(source='poll.description')
    passed_at = serializers.DateTimeField()
    questions = AnsweredQuestionSerializer(many=True, source='poll.questions')
