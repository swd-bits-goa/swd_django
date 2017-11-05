from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'home.html',{})


def login_success(request):
    return HttpResponse("Success!")
