from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student

def index(request):
    return render(request, 'home1.html',{})


def login_success(request):
    return HttpResponse("Success!")

@login_required
def dashboard(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, "index.html", context)

def profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    print(student.name)
    return render(request, "profile.html", context)

def loginform(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin')
            return redirect('dashboard')

    return render(request, "sign-in.html", {})

def logoutform(request):
    logout(request)
    return render(request, "logout.html", {})
    
