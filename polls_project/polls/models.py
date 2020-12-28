from django.db import models
from django.conf import settings


class Poll(models.Model):
    """Модель опроса"""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор опроса',
        on_delete=models.CASCADE,
        related_name='polls'
    )
    title = models.CharField('Название опроса', max_length=512)
    description = models.TextField('Описание опроса')
    started_at = models.DateTimeField('Дата начала опроса', auto_now_add=True)
    stopped_at = models.DateTimeField('Дата завершения опроса', blank=True, null=True)

    class Meta:
        db_table = 'polls'

    def __str__(self) -> str:
        return f'{self.author.username}   {self.pk}:{self.title}'


class PassedPoll(models.Model):
    """Модель пройденного опроса"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь, прошедший опрос',
        on_delete=models.SET_NULL,
        related_name='passed_polls',
        blank=True, null=True
    )
    poll = models.ForeignKey(Poll, verbose_name='Опрос', on_delete=models.CASCADE,
                             related_name='passed_polls')
    passed_at = models.DateTimeField('Дата прохождения', auto_now_add=True)

    class Meta:
        db_table = 'passed_polls'

    def __str__(self) -> str:
        if self.user:
            return f'{self.user.username}   {self.poll}   {self.pk}'
        return f'{self.poll}   {self.pk}'


class Question(models.Model):
    """Модель вопроса"""
    TEXT_CHOICE, SINGLE_CHOICE, MULTIPLE_CHOICE = range(3)
    QUESTION_TYPES = (
        (TEXT_CHOICE, 'Вопрос с текстовым ответ'),
        (SINGLE_CHOICE, 'Вопрос с одним вариантом ответа'),
        (MULTIPLE_CHOICE, 'Вопрос с несколькими вариантами ответов')
    )

    poll = models.ForeignKey(Poll, verbose_name='Опрос', on_delete=models.CASCADE,
                             related_name='questions')
    text = models.TextField('Текст вопроса')
    question_type = models.IntegerField(
        ('Тип вопроса: '
        '0 - текстовый '
        '1 - с одним вариантом ответа '
        '2 - с несколькими вариантами ответов'),
        choices=QUESTION_TYPES
    )

    class Meta:
        db_table = 'questions'

    def __str__(self) -> str:
        return f'{self.poll}   {self.pk}:{self.text}, {self.question_type}'


class Choice(models.Model):
    """Модель варианта ответа для вопросов с выбором ответов"""
    question = models.ForeignKey(Question, verbose_name='Вопрос',
                                 on_delete=models.CASCADE, related_name='choices')
    text = models.CharField('Вариант ответа', max_length=512)

    class Meta:
        db_table = 'choices'

    def __str__(self) -> str:
        return f'{self.question}   {self.pk}:{self.text}'


class Answer(models.Model):
    """Модель ответа на вопрос"""
    passed_poll = models.ForeignKey(PassedPoll, verbose_name='Пройденный опрос',
                                    on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='answers', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=512, blank=True, null=True)
    choices = models.ManyToManyField(Choice, verbose_name='Варианты ответа',
                                    related_name='answers')

    class Meta:
        db_table = 'answers'

    def __str__(self) -> str:
        return f'{self.passed_poll}   {self.pk}'
