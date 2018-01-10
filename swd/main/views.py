from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, MessOptionOpen, MessOption, Leave, Bonafide, Faculty, Warden
from datetime import date, datetime
from .forms import MessForm, LeaveForm, BonafideForm
from django.contrib import messages
from django.utils.timezone import make_aware

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from easy_pdf.views import PDFTemplateView

from braces import views

from urllib.request import urlopen
from urllib.parse import urlencode

from django.contrib.auth.models import User

import re

def index(request):
    return render(request, 'home1.html',{})


def login_success(request):
    return HttpResponse("Success!")


@login_required
def dashboard(request):
    student = Student.objects.get(user=request.user)

    leaves = Leave.objects.filter(student=student).last()
    bonafides = Bonafide.objects.filter(student=student).last()

    context = {
        'student': student,
        'leaves': leaves,
        'bonafides': bonafides,
    }
    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gte=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        form = MessForm(request.POST)
        context = {
            'option': 0,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            }
    elif messopen and messoption:
        context = {
            'option': 1,
            'mess': messoption[0].mess,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            }
    else:
        context = {
            'option': 2,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            }


    return render(request, "dashboard.html", context)


@login_required
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
        print(username, password)
        if user is None:
            try:
                with urlopen("http://10.10.10.20/auth.php?" + urlencode({'u': username, 'p': password}), timeout=5) as authfile:
                    string = authfile.read()
                    print(string)
                    print(re.findall("'([^']*)'", string)[0])
                    if string=="b'true'":
                        try:
                            u = User.objects.get(username__exact=username)
                            u.set_password(password)
                            u.save()
                        except:
                            print('user fail')
                            pass
                    else:
                        print("User doesn't exist")
            except:
                print("URL not reachable")
                    
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin')
            if user.groups.filter(name='warden').exists():
                return redirect('/warden')
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

    context = {'student': student}

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        form = MessForm(request.POST)
        context = {'option': 0, 'form': form, 'dateClose': messopen[0].dateClose, 'student': student}
    elif messopen and messoption:
        context = {'option': 1, 'mess': messoption[0].mess, 'student': student}
    else:
        context = {'option': 2, 'student': student}

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
    form = BonafideForm()
    context = {
        'option': 0,
        'student': student,
        'form': form
    }
    bonafideContext = {
        'bonafides': Bonafide.objects.filter(student=student),
    }

    if request.POST:
        form = BonafideForm(request.POST)
        if form.is_valid():
            bonafideform = form.save(commit=False)
            bonafideform.reqDate = datetime.today()
            bonafideform.student = student
            bonafideform.save()

            context = {
                'option': 1,
            }
        else:
            context = {
                'option': 2,
            }
            print(form.errors)

    return render(request, "certificates.html", dict(context, **bonafideContext))

def bonafidepdf(request):
    response = HttpResponse(content_type='application/pdf')
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    text = '''
    '''
    p.drawString(100, 700, text)
    p.showPage()
    p.save()
    return response

def printBonafide(request):
    pass

class BonafidePDFView(views.LoginRequiredMixin, views.PermissionRequiredMixin, PDFTemplateView):
    permission_required = "auth.change_user"
    context_object_name = 'contexts'
    template_name = 'bonafidepdf.html'

    def get_context_data(self, **kwargs):
        b = Bonafide.objects.get(pk=self.request.GET.get('bonafide'))
        b.printed = True
        b.save()

        return super(BonafidePDFView, self).get_context_data(
            bonafide=Bonafide.objects.get(pk=self.request.GET.get('bonafide')),
            date = datetime.today().date(),
            pagesize='A4',
            title='Bonafide Certificates',
            **kwargs
        )

def is_member(user):
    return user.groups.filter(name='warden').exists()

@login_required
@user_passes_test(is_member)
def warden(request):
    warden = Warden.objects.get(faculty__user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel='AH4').order_by('approved', '-id')
    context = {
        'option':1,
        'warden': warden,
        'leaves': leaves,
    }
    return render(request, "warden.html", context)

@login_required
@user_passes_test(is_member)
def wardenapprove(request, leave):
    leave = Leave.objects.get(id=leave)
    warden = Warden.objects.get(faculty__user=request.user)
    context = {
        'option': 2,
        'warden': warden,
        'leave': leave,
    }

    if request.POST:
        approved = request.POST.getlist('group1')
        print(approved)
        comment = request.POST.get('comment')

        if '1' in approved:
            leave.approved=True
            leave.approvedBy = warden
        elif '2' in approved:
            leave.approved=False
            leave.approvedBy = warden
        else:
            leave.approved=False
            leave.approvedBy = None

        leave.comment = comment
        leave.save()
        return redirect('warden')

    return render(request, "warden.html", context)
