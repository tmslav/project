__author__ = 'tomislav'
from .views import Login, Main, upload, items, results, last, logout_1
from django.contrib.auth import logout
from django.conf.urls import url
from django.shortcuts import render, redirect

urlpatterns = [
    url(r"^$", Login.as_view()),
    url(r"^app/$", Main.as_view()),
    url("^upload/$", upload),
    url(r'^items/(?P<id>\d+)/$', items),
    url(r'^results/$', results),
    url(r'^last/(?P<number>\d+)/$', last),
    url(r'^logout$', logout_1)
]
