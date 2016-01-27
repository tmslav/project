__author__ = 'tomislav'
from .views import Login,Main
from django.conf.urls import url

urlpatterns = [
    url(r"^$",Login.as_view()),
    url(r"^app/$",Main.as_view())
    ]
