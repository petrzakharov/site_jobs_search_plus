from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render


def custom_handler404(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена, упс!</h1>')


def custom_handler500(request):
    return HttpResponseServerError('<h1>Произошла ошибка на сервере, упс!</h1>')
