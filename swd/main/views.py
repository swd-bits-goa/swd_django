from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, MessOptionOpen, MessOption, Leave, Bonafide, Warden, DayPass, MessBill
from datetime import date, datetime, timedelta
from .forms import MessForm, LeaveForm, BonafideForm, DayPassForm
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.files.storage import FileSystemStorage
import random
import string
from braces import views

from django.contrib.auth.models import User

from calendar import monthrange

import re

def index(request):
    return render(request, 'home1.html',{})


def login_success(request):
    return HttpResponse("Success!")


@login_required
def dashboard(request):
    print(request.user)
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))

    context = {
        'student': student,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
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
            'daypasss': daypasss,
            }
    elif messopen and messoption:
        context = {
            'option': 1,
            'mess': messoption[0].mess,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            }
    else:
        context = {
            'option': 2,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            }


    return render(request, "dashboard.html", context)


@login_required
def profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    print(student)
    return render(request, "profile.html", context)

@login_required
def updatephoto(request):
    im = request.FILES['image']
    fs = FileSystemStorage()
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    print(name)
    path = "static/img/students/"+name+request.POST.get('extension')
    print(path)
    filename = fs.save(path, im)
    uploaded_file_url = "/"+fs.url(filename)
    student = Student.objects.get(user=request.user)
    student.photoURL = uploaded_file_url
    student.save()
    return HttpResponse(uploaded_file_url)

def loginform(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(username, password)
        #user = True 
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin')
            if Warden.objects.filter(user=request.user):
                return redirect('/warden')
            return redirect('dashboard')
        else:
            print('Not able to authenticate')

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
    edit = 0

    if request.GET:
        edit = request.GET.get('edit')

    if (messopen and not messoption and datetime.today().date() < messopen[0].dateClose) or (messopen and edit):
        form = MessForm(request.POST)
        context = {'option': 0, 'form': form, 'dateClose': messopen[0].dateClose, 'student': student}
    elif messopen and messoption:
        context = {'option': 1, 'mess': messoption[0].mess, 'student': student}
    else:
        context = {'option': 2, 'student': student}

    if request.POST:
        mess = request.POST.get('mess')
        if edit: messoption.delete()
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

# class BonafidePDFView(views.LoginRequiredMixin, views.PermissionRequiredMixin, PDFTemplateView):
#     permission_required = "auth.change_user"
#     context_object_name = 'contexts'
#     template_name = 'bonafidepdf.html'

#     def get_context_data(self, **kwargs):
#         b = Bonafide.objects.get(pk=self.request.GET.get('bonafide'))
#         b.printed = True
#         b.save()

#         return super(BonafidePDFView, self).get_context_data(
#             bonafide=Bonafide.objects.get(pk=self.request.GET.get('bonafide')),
#             date = datetime.today().date(),
#             pagesize='A4',
#             title='Bonafide Certificates',
#             **kwargs
#         )

def is_warden(user):
    return False if not Warden.objects.filter(user=user) else True

@login_required
@user_passes_test(is_warden)
def warden(request):
    warden = Warden.objects.get(user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel=warden.hostel).order_by('approved', '-id')
    daypasss = DayPass.objects.filter(student__hostelps__hostel=warden.hostel).order_by('approved', '-id')
    context = {
        'option':1,
        'warden': warden,
        'leaves': leaves,
        'daypasss': daypasss
    }
    return render(request, "warden.html", context)

@login_required
@user_passes_test(is_warden)
def wardenleaveapprove(request, leave):
    leave = Leave.objects.get(id=leave)
    warden = Warden.objects.get(user=request.user)
    daypasss = DayPass.objects.filter(student__hostelps__hostel=warden.hostel).order_by('approved', '-id')

    context = {
        'option': 2,
        'warden': warden,
        'leave': leave,
        'daypasss' : daypasss,
    }

    if request.POST:
        approved = request.POST.getlist('group1')
        print(approved)
        comment = request.POST.get('comment')

        if '1' in approved:
            leave.approved=True
            leave.disapproved = False
            leave.inprocess = False
            leave.approvedBy = warden
        elif '2' in approved:
            leave.disapproved=True
            leave.approved = False
            leave.inprocess = False
            leave.approvedBy = warden
        else:
            leave.inprocess = True
            leave.approved = False
            leave.disapproved = False
            leave.approvedBy = None

        leave.comment = comment
        leave.save()
        return redirect('warden')

    return render(request, "warden.html", context)

@login_required
@user_passes_test(is_warden)
def wardendaypassapprove(request, daypass):
    daypass = DayPass.objects.get(id=daypass)
    warden = Warden.objects.get(user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel=warden.hostel).order_by('approved', '-id')
    context = {
        'option': 3,
        'warden': warden,
        'daypass': daypass,
        'leaves' : leaves,
    }

    if request.POST:
        approved = request.POST.getlist('group1')
        print(approved)
        comment = request.POST.get('comment')

        if '1' in approved:
            daypass.approved=True
            daypass.disapproved = False
            daypass.inprocess = False
            daypass.approvedBy = warden
        elif '2' in approved:
            daypass.disapproved=True
            daypass.approved = False
            daypass.inprocess = False
            daypass.approvedBy = warden
        else:
            daypass.inprocess = True
            daypass.approved = False
            daypass.disapproved = False
            daypass.approvedBy = None

        daypass.comment = comment
        daypass.save()
        return redirect('warden')

    return render(request, "warden.html", context)


@login_required
def daypass(request):
    student = Student.objects.get(user=request.user)
    form = DayPassForm()
    context = {
        'option' : 0,
        'student': student,
        'form': form
    }

    daypassContext = {
        'daypass': DayPass.objects.filter(student=student),
    }

    if request.POST:
        form = DayPassForm(request.POST)
        if form.is_valid():
            daypassform = form.save(commit=False)
            date = datetime.strptime(request.POST.get('date'), '%d %B, %Y').date()
            time = datetime.strptime(request.POST.get('time'), '%H:%M').time()
            dateTime = datetime.combine(date, time)
            daypassform.dateTime = make_aware(dateTime)
            daypassform.student = student
            daypassform.save()

            context = {
                'option': 1,
                'date': request.POST.get('date'),

            }
        else:
            context = {
                'option': 2,
            }
            print(form.errors)
    return render(request, "daypass.html", dict(context, **daypassContext))

@user_passes_test(lambda u: u.is_superuser)
def messbill(request):
    selected = request.GET['ids']
    values = [x for x in selected.split(',')]
    if request.POST:
        import xlwt
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=rebate.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("Rebate")

        row_num = 0

        columns = [
            (u"Name", 6000),
            (u"ID", 6000),
            (u"Amount", 3000),
            (u"Rebate", 3000),
            (u"Final Amount", 3000),
        ]

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            # set column width
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        print(request.POST.get('start_date'))
        start_date = datetime.strptime(request.POST.get('start_date'), '%d %B, %Y').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%d %B, %Y').date()

        messbill = MessBill.objects.first()
        amount = messbill.amount
        rebate = messbill.rebate

        end_date = end_date if end_date<date.today() else date.today()

        days = end_date - start_date
        days = days.days

        for k in values:
            obj = Student.objects.get(bitsId=k)
            row_num += 1
            leaves = Leave.objects.filter(student=obj)
            noofdays = 0
            for leave in leaves:
                if leave.approved == True:
                    if leave.dateTimeStart.date() > start_date and leave.dateTimeStart.date() < end_date:
                        noofdays += abs(leave.dateTimeStart.date() -
                                        leave.dateTimeEnd.date()).days + 1
                        print(noofdays)
            finalamt = amount * days - rebate * noofdays
            row = [
                obj.name,
                obj.bitsId,
                amount * days,
                rebate * noofdays,
                finalamt
            ]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response

    return render(request, "messbill.html", {})
