from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index_page, name='home'),
    path('profile/', profile, name='profile'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('votes/', votes_view, name='votes'),
    path('vote_create/', vote_create, name='vote_create'),
    path('vote_created/', vote_created, name='vote_created'),
    path('vote/<int:id>/', vote_view, name='vote'),
]
