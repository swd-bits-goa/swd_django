from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, MessOptionOpen, MessOption, Leave
from datetime import date, datetime
from .forms import MessForm, LeaveForm
from django.contrib import messages
from django.utils.timezone import make_aware

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


@login_required
def profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    print(student.name)
    return render(request, "profile.html", context)


@login_required
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


@login_required
def logoutform(request):
    logout(request)
    return render(request, "logout.html", {})


@login_required
def messoption(request):
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gte=date.today())
    student = Student.objects.get(user=request.user)

    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    context = {}

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        form = MessForm(request.POST)
        context = {'option': 0, 'form': form, 'dateClose': messopen[0].dateClose}
    elif messopen and messoption:
        context = {'option': 1, 'mess': messoption[0].mess}
    else:
        context = {'option': 2}

    if request.POST:
        mess = request.POST.get('mess')
        messoptionfill = MessOption(student=student, monthYear=messopen[0].monthYear, mess=mess)
        messoptionfill.save()
        return redirect('messoption')

    
    return render(request, "mess.html", context)


@login_required
def leave(request):
    student = Student.objects.get(user=request.user)
    form = LeaveForm()
    context = {
        'option' : 0,
        'student': student,
        'form': form
    }

    leaveContext = {
        'leaves': Leave.objects.filter(student=student),
    }

    if request.POST:
        form = LeaveForm(request.POST)
        if form.is_valid():
            leaveform = form.save(commit=False)
            dateStart = datetime.strptime(request.POST.get('dateStart'), '%d %B, %Y').date()
            timeStart = datetime.strptime(request.POST.get('timeStart'), '%H:%M').time()
            dateTimeStart = datetime.combine(dateStart, timeStart)
            dateEnd = datetime.strptime(request.POST.get('dateEnd'), '%d %B, %Y').date()
            timeEnd = datetime.strptime(request.POST.get('timeEnd'), '%H:%M').time()
            dateTimeEnd = datetime.combine(dateEnd, timeEnd)
            leaveform.dateTimeStart = make_aware(dateTimeStart)
            leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            leaveform.student = student
            leaveform.save()

            context = {
                'option': 1,
                'dateStart': request.POST.get('dateStart'),
                'dateEnd': request.POST.get('dateEnd'),
                'timeStart': request.POST.get('timeStart'),
                'timeEnd': request.POST.get('timeEnd'),
            }
        else:
            context = {
                'option': 2,
            }
            print(form.errors)
    return render(request, "leave.html", dict(context, **leaveContext))


@login_required
def certificates(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, "index.html", context)
