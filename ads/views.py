from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def homepage_view(request):
  return HttpResponse('Главная страница КУПИ-ПРОДАЙ')
