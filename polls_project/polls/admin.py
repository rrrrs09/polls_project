from django.contrib import admin
from django.db import models

from .models import Poll, PassedPoll, Question, Choice, Answer

admin.site.register(Poll)
admin.site.register(PassedPoll)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)

