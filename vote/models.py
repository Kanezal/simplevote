from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

# Модели для приложения голосования

class Vote(models.Model):
    """
    Модель для голосования. Содержит заголовок, видимость, автора и время создания.
    """
    title = models.CharField(max_length=4096)  # Заголовок голосования
    visible = models.BooleanField(default=False)  # Видимость голосования
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)  # Автор голосования
    created = models.DateTimeField(auto_now_add=True)  # Время создания голосования

    def __str__(self):
        return self.title


class Choice(models.Model):
    """
    Модель для варианта ответа в голосовании. Содержит вопрос, к которому относится, заголовок и блокировку других ответов.
    """
    question = models.ForeignKey(to=Vote, on_delete=models.DO_NOTHING)  # Вопрос, к которому относится вариант ответа
    title = models.CharField(max_length=4096)  # Заголовок варианта ответа
    lock_other = models.BooleanField(default=False)  # Блокировка других ответов при выборе этого

    def __str__(self):
        return self.title


class Answer(models.Model):
    """
    Модель для ответа пользователя. Содержит пользователя, вопрос, выбранный вариант ответа и время создания.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)  # Пользователь, который ответил
    question = models.ForeignKey(Vote, on_delete=models.DO_NOTHING)  # Вопрос, на который ответил пользователь
    choice = models.ForeignKey(Choice, on_delete=models.DO_NOTHING)  # Выбранный вариант ответа
    created = models.DateTimeField(auto_now_add=True)  # Время создания ответа

    def __str__(self):
        return self.choice.title