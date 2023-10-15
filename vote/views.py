import datetime

from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .forms import *
from .models import *
from django.http import HttpResponseRedirect
from django.http import Http404


def get_base_context():
    """
    Функция для получения базового контекста, который используется во всех представлениях.
    Возвращает словарь с меню и текущим временем.
    """
    context = {
        'menu': [
            {'link': '/', 'text': 'Главная'},
            {'link': '/votes/', 'text': 'Все голосования'},
        ],
        'current_time': datetime.datetime.now(),
    }
    return context


def profile(request):
    """
    Функция для отображения профиля пользователя.
    """
    cxt = get_base_context()
    return render(request, 'profile.html', cxt)


class RegisterUser(CreateView):
    """
    Класс для регистрации нового пользователя.
    """
    form_class = RegisterUserForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return get_base_context() | dict(list(context.items())) | {'title': "Регистрация"}

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    """
    Класс для авторизации пользователя.
    """
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return get_base_context() | dict(list(context.items())) | {'title': "Войти"}

    def get_success_url(self):
        return reverse_lazy('home')


def index_page(request):
    """
    Функция для отображения главной страницы.
    """
    context = get_base_context()
    context['title'] = 'Главная страница - simple votings'
    context['main_header'] = 'Simple votings'
    return render(request, 'index.html', context)


def logout_user(request):
    """
    Функция для выхода пользователя из системы.
    """
    logout(request)
    return redirect('login')


def votes_view(request):
    """
    Функция для отображения всех голосований.
    """
    # page = int(
    #     request.GET.get('page') if request.GET.get('page') != None else 1)
    #
    # all_votes = Vote.objects.order_by('-created')[
    #             (page - 1) * 10:(page - 1) * 10 + 10]

    all_votes = Vote.objects.order_by('-created')

    ctx = {
        "votes": all_votes,
        "votes_num": len(all_votes),
    }
    return render(request, 'votes.html', context=(get_base_context() | ctx | {'title': "Голосования"}))


def vote_create(request):
    """
    Функция для отображения страницы после успешного создания голосования.
    """
    form_valid = True

    if request.method == "POST":
        choices = int(request.POST.get("choices_count"))
        for i in range(1, choices + 1):
            if request.POST.get(str(i)) == "":
                form_valid = False

        if form_valid and choices != 0:
            f_vote = VoteCreateForm(request.POST)
            choices = int(request.POST.get("choices_count"))
            if f_vote.is_valid():
                new_vote = Vote(title=f_vote.cleaned_data['title'],
                                visible=True,
                                author=request.user)
                new_vote.save()

                for i in range(1, choices + 1):
                    new_choice = Choice(question=new_vote,
                                        title=request.POST.get(str(i)),
                                        lock_other=("1" == str(request.POST.get("lock_other"))))
                    new_choice.save()

                return HttpResponseRedirect('/vote_created/')
            else:
                form_valid = False
        else:
            f_vote = VoteCreateForm()
    else:
        f_vote = VoteCreateForm()

    ctx = {
        'form': f_vote,
        'form_valid': form_valid
    }
    return render(request, 'vote_create.html',
                  context=(get_base_context() | ctx | {'title': "Создание голосования"}))


def vote_created(request):
    """
    Функция для отображения страницы после успешного создания голосования.
    """
    return render(request, 'vote_created.html', context=get_base_context() | {'title': "Голосование создано"})


def vote_view(request):
    """
    Функция для отображения конкретного голосования и обработки ответов пользователя.
    """
    form_valid = True

    # Getting the vote id from the request
    vote_id = request.GET.get('id')
    if vote_id is not None and vote_id != "":
        # Checking if the user has already answered the vote
        if len(Answer.objects.filter(question=Vote.objects.filter(id=vote_id)[0], user=request.user)) == 0:
            if request.method == "POST":
                # Getting the number of choices for this vote
                count_choices = len(Choice.objects.filter(question_id=vote_id))

                # Checking if the form is valid
                if len(list(request.POST.items())) == 2 and list(request.POST.items())[1][1] == "":
                    form_valid = False

                # Getting the choice made by the user from the request
                radio_choice = request.POST.get("radio_choice")

                # If form is valid, save the user's answer
                if form_valid:
                    if len(radio_choice) == 0:
                        for choice in list(request.POST.items())[2:]:
                            new_answer = Answer(user=request.user,
                                                question=Vote.objects.get(id=vote_id),
                                                choice=Choice.objects.get(id=str(choice[0])),) # Creating the answer instance
                            new_answer.save() # Saving the answer into the database
                    else:
                        choice = request.POST.get("radio_choice")
                        new_answer = Answer(user=request.user,
                                            question=Vote.objects.get(id=vote_id),
                                            choice=Choice.objects.get(id=str(choice))) # Creating the answer instance
                        new_answer.save() # Saving the answer into the database

                    # Redirecting the user to the vote page
                    return HttpResponseRedirect(f'/vote/?id={vote_id}')
                else:
                    ctx = {
                        'vote_passed': False,
                        'form_valid': form_valid,
                        'vote_title': Vote.objects.filter(id=vote_id)[0],
                        'vote_choices': Choice.objects.filter(question_id=vote_id),
                        'alert': "Вы не выбрали ни один вариант голосования",
                    }
                    # Rendering the vote page with an alert for not choosing any option
                    return render(request, 'vote.html',
                                  context=(get_base_context() | ctx | {'title': "Голосование"}))
        else:
            # Getting all answers for this vote
            all_answers = Answer.objects.filter(question=Vote.objects.get(id=vote_id))
            variants_choices = []
            for answer in all_answers:
                if answer.choice_id not in variants_choices:
                    variants_choices.append(answer.choice_id)
            variants_choices.sort()

            # Creating a dictionary to store the voting statistics
            statistics = {}
            for choice in variants_choices:
                statistics[str(Choice.objects.get(id=choice).title)] = [len(list(Answer.objects.filter(choice=choice))),
                                                                        len(list(Answer.objects.filter(choice=choice, user=request.user)))]
            ctx = {
                'vote_passed': True,
                'form_valid': form_valid,
                'vote_title': Vote.objects.filter(id=vote_id)[0],
                'vote_choices': Choice.objects.filter(question_id=vote_id),
                'statistics': statistics,
            }
            # Rendering the vote page with voting statistics
            return render(request, 'vote.html',
                          context=(get_base_context() | ctx | {'title': "Голосование"}))
        ctx = {
            'vote_passed': False,
            'form_valid': form_valid,
            'vote_title': Vote.objects.filter(id=vote_id)[0],
            'vote_choices': Choice.objects.filter(question_id=vote_id)
        }
        # Rendering the vote page
        return render(request, 'vote.html',
                      context=(get_base_context() | ctx | {'title': "Голосование"}))
    else:
        # No vote id found in the request, raising a 404 error
        raise Http404
