from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.views.decorators.csrf import csrf_protect
from datetime import date, datetime, timedelta
from .forms import MessForm, LeaveForm, BonafideForm, DayPassForm
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.conf import settings
from tools.utils import gen_random_datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import xlrd, xlwt

from braces import views

from django.contrib.auth.models import User

from calendar import monthrange
from dateutil import rrule
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Q
from .models import BRANCH, HOSTELS

import swd.config as config

import re
import xlrd
import xlwt
import os
import tempfile
import json

from calendar import monthrange


def noPhD(func):
    def check(request, *args, **kwargs):
        student = Student.objects.get(user=request.user)
        if student.nophd():
            return redirect("/dashboard/")
        return func(request, *args, **kwargs)
    return check

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
                return redirect('/admin')
        if Warden.objects.filter(user=request.user):
            return redirect('/warden')
        if HostelSuperintendent.objects.filter(user=request.user):
            return redirect('/hostelsuperintendent')
        return redirect('dashboard')
    else:
        notice_list = Notice.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(notice_list, 5)
        try:
            notices = paginator.page(page)
        except PageNotAnInteger:
            notices = paginator.page(1)
        except EmptyPage:
            notices = paginator.page(paginator.num_pages)

        context = {
        'queryset' : notices,
        }
        return render(request, 'home1.html',context)


def login_success(request):
    return HttpResponse("Success!")

# @login_required
# def studentimg(request):
#     url = Student.objects.get(user=request.user).profile_picture
#     print(url)
#     ext = url.name.split('.')[-1]

#     try:
#         with open(url.name, "rb") as f:
#             return HttpResponse(f.read(), content_type="image/"+ext)
#     except IOError:
#         with open("assets/img/profile-swd.jpg", "rb") as f:
#             return HttpResponse(f.read(), content_type="image/jpg")

@login_required
def dashboard(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    address = student.address
    tees = TeeAdd.objects.filter(available=True).order_by('-pk')
    items = ItemAdd.objects.filter(available=True)
    teesj = TeeAdd.objects.filter(available=True).values_list('title')
    notice_list = Notice.objects.all().order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(notice_list, 10)
    try:
        notices = paginator.page(page)
    except PageNotAnInteger:
        notices = paginator.page(1)
    except EmptyPage:
        notices = paginator.page(paginator.num_pages)

    #dues
    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=datetime.today())
    #messopen = messopen.exclude(dateOpen__gt=date.today())
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
            'address': address
            }
    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

    context = {
            'option': option,
            'mess': mess,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            'balance': balance,
            'address': address,
            'queryset' : notices,
            'student': student,
            'tees': tees,
            'items': items
            }

    return render(request, "dashboard.html", context)


@login_required
def profile(request):
    if is_warden(request.user):
        warden = Warden.objects.get(user=request.user)
        context = {
            'option1' : 'wardenbase.html',
            'warden' : warden,
        }
    elif is_hostelsuperintendent(request.user):
        hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
        context = {
            'option1' : 'superintendentbase.html',
            'hostelsuperintendent' : hostelsuperintendent
        }
    else:
        student = Student.objects.get(user=request.user)
        hostelps = HostelPS.objects.get(student=student)
        leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
        daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
        bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
        #dues
        try:
            lasted = DuesPublished.objects.latest('date_published').date_published
        except:
            lasted = datetime(year=2004, month=1, day=1) # Before college was founded

        otherdues = Due.objects.filter(student=student)
        itemdues = ItemBuy.objects.filter(student=student,
                                        created__gte=lasted)
        teedues = TeeBuy.objects.filter(student=student,
                                        created__gte=lasted)
        total_amount = 0
        for item in itemdues:
            if item is not None:
                total_amount += item.item.price
        for tee in teedues:
            if tee is not None:
                total_amount += tee.totamt
        for other in otherdues:
            if other is not None:
                total_amount += other.amount
        balance = float(22000) - float(total_amount)

        #mess
        messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
        messopen = messopen.exclude(dateOpen__gt=date.today())
        if messopen:
            messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

        if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
            option = 0
            mess = 0
        elif messopen and messoption:
            option = 1
            mess = messoption[0]
        else:
            option = 2
            mess = 0

        context = {
            'option1' : 'base.html',
            'student': student,
            'option': option,
            'mess': mess,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            'balance': balance,
            'hostelps':hostelps,
        }

        if request.POST:
            address = request.POST.get('address')

            addr_request = AddressChangeRequest(student=student, new_address=address)
            addr_request.save()

            return HttpResponse("{ status: 'ok' }")

    return render(request, "profile.html", context)


@user_passes_test(lambda a: a.is_superuser)
def address_approval_dashboard(request):
    if request.POST:
        approve = AddressChangeRequest.objects.get(id=request.POST["request_id"])

        if request.POST["approved"] == "false":
            approve.reject()
        else:
            approve.approve()

    address_reqs = AddressChangeRequest.objects.filter(resolved=False)

    return render(request, "address_dashboard.html", {
        "requests": address_reqs
    })


@csrf_protect
def loginform(request):

    if request.user.is_authenticated:
        if request.user.is_staff:
                return redirect('/admin')
        if Warden.objects.filter(user=request.user):
            return redirect('/warden')
        if HostelSuperintendent.objects.filter(user=request.user):
            return redirect('/hostelsuperintendent')
        return redirect('dashboard')

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin')
            if Warden.objects.filter(user=request.user):
                return redirect('/warden')
            if HostelSuperintendent.objects.filter(user=request.user):
                return redirect('/hostelsuperintendent')
            return redirect('dashboard')
        else:
            messages.add_message(request, messages.INFO,  "Incorrect username or password", extra_tags='red')
            print('Not able to authenticate')

    return render(request, "sign-in.html", {})


@login_required
def logoutform(request):
    logout(request)
    return render(request, "logout.html", {})


@login_required
@noPhD
def messoption(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())

    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    # dues
    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    edit = 0

    if request.GET:
        edit = request.GET.get('edit')

    if (messopen and not messoption and datetime.today().date() < messopen[0].dateClose) or (messopen and edit):
        form = MessForm(request.POST)
        context = {
            'option': 0,
            'form': form,
            'dateClose': messopen[0].dateClose,
            'student': student,
            'balance': balance,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,}
    elif messopen and messoption:
        context = {
            'option': 1,
            'mess': messoption[0],
            'student': student,
            'balance': balance,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,}
    else:
        context = {
            'option': 2,
            'student': student,
            'leaves': leaves,
            'balance': balance,
            'bonafides': bonafides,
            'daypasss': daypasss,
            }
    
    vacations = VacationDatesFill.objects.filter(
        dateClose__gte=date.today(), dateOpen__lte=date.today())
    errors = []
    if vacations:
        vacation_open = vacations[0]
        student_vacation = Leave.objects.filter(
            student=student,
            reason=vacation_open.description)
        if student_vacation:
            student_vacation = student_vacation[0]
        context['vacation'] = vacation_open
        context['student_vacation'] = student_vacation

    if request.POST:
        # Vacation Details Filling when availaible
        created = False
        if vacations:
            dateStart = datetime.strptime(request.POST.get('dateStart'), '%d %B, %Y').date()
            timeStart = gen_random_datetime().time()
            dateTimeStart = make_aware(datetime.combine(dateStart, timeStart))
            dateEnd = datetime.strptime(request.POST.get('dateEnd'), '%d %B, %Y').date()
            timeEnd = gen_random_datetime().time()
            dateTimeEnd = make_aware(datetime.combine(dateEnd, timeEnd))
            
            if not vacation_open.check_date_in_range(dateTimeEnd):
                errors.append("End Date Time should be within specified range.")
            if not vacation_open.check_date_in_range(dateTimeStart):
                errors.append("Start Date Time should be within specified range.")
            if vacation_open.check_start_end_dates_in_range(dateTimeStart, dateTimeEnd):
                if edit:
                    student_vacation.delete()
                created, obj = vacation_open.create_vacation(
                    student, dateTimeStart, dateTimeEnd)
                if not created:
                    errors.append(obj)
            context['errors'] = errors

        if (vacations.count() and len(errors) == 0) or (vacations.count() == 0) or (edit):
            print("Inside Mess Filling")
            # Mess Option Filling
            mess = request.POST.get('mess')
            if edit:
                messoption.delete()
            messoptionfill = MessOption(
                student=student,
                monthYear=messopen[0].monthYear,
                mess=mess)
            messoptionfill.save()

        if created or (vacations.count() == 0):
            return redirect('messoption')

    return render(request, "mess.html", context)


@login_required
@noPhD
def leave(request):
    dashboard
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

        #dues
    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    form = LeaveForm()
    context = {
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        'option1' : 0,
        'balance' : balance,
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
            leaveform.corrPhone = request.POST.get('phone_number')
            leaveform.dateTimeStart = make_aware(dateTimeStart)
            leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            leaveform.student = student
            print(request.POST.get('consent'))
            leaveform.save()
            if config.EMAIL_PROD:
                email_to=[Warden.objects.get(hostel=HostelPS.objects.get(student=student).hostel).email]
            else:
                email_to=["spammailashad@gmail.com"]                                                                     # For testing
            mailObj=Leave.objects.latest('id')
            mail_subject="New Leave ID: "+ str(mailObj.id)
            if mailObj.student.parentEmail is None:
                parentEmail = "No parent mail found"
            else:
                parentEmail = mailObj.student.parentEmail
            if mailObj.student.parentName is None:
                parentName = "Parent name is null"
            else:
                parentName = mailObj.student.parentName
            if mailObj.student.parentPhone is None:
                parentPhone = "No parent phone"
            else:
                parentPhone = mailObj.student.parentPhone
                
            mail_message="Leave Application applied by "+ mailObj.student.name +" with leave id: " + str(mailObj.id) + ".\n"
            mail_message=mail_message + "Parent name: " + parentName + "\nParent Email: "+ parentEmail + "\nParent Phone: " + parentPhone
            mail_message=mail_message + "\nConsent type: " + mailObj.consent
            send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)

            context = {
                'option': option,
                'mess': mess,
                'leaves': leaves,
                'bonafides': bonafides,
                'balance' : balance,
                'daypasss': daypasss,
                'option1': 1,
                'dateStart': request.POST.get('dateStart'),
                'dateEnd': request.POST.get('dateEnd'),
                'timeStart': request.POST.get('timeStart'),
                'timeEnd': request.POST.get('timeEnd'),
            }
        else:
            context = {
                'option': option,
                'mess': mess,
                'leaves': leaves,
                'bonafides': bonafides,
                'balance' : balance,
                'daypasss': daypasss,
                'option1': 2,
                'form': form
            }
            print(form.errors)
    return render(request, "leave.html", dict(context, **leaveContext))


@login_required
def certificates(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))

#dues
    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

    form = BonafideForm()
    context = {
        'option': option,
        'mess': mess,
        'option1': 0,
        'student': student,
        'balance': balance,
        'form': form,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
    }
    queryset=Bonafide.objects.filter(student=student);
    bonafideContext = {
        'bonafides': queryset,
    }
    sem_count=[0,0]
    for bonafide in queryset:
        if datetime.now().year==bonafide.reqDate.year:
            sem_count[(int(bonafide.reqDate.month)-1)//6]+=1
    if sem_count[(datetime.now().month-1)//6] < 3:
        if request.POST:
            form = BonafideForm(request.POST)
            if form.is_valid():
                bonafideform = form.save(commit=False)
                bonafideform.reqDate = date.today()
                bonafideform.student = student
                bonafideform.save()

                context = {
                    'option1': 1,
                    'option': option,
                    'mess': mess,
                    'balance': balance,
                    'student': student,
                    'form': form,
                    'leaves': leaves,
                    'bonafides': bonafides,
                    'daypasss': daypasss,
                }
            else:
                context = {
                    'option': option,
                    'mess': mess,
                    'option1': 2,
                    'student': student,
                    'form': form,
                    'leaves': leaves,
                    'balance': balance,
                    'bonafides': bonafides,
                    'daypasss': daypasss,
                }
    else:
        context = {
              'option1': 3,
            }

    return render(request, "certificates.html", dict(context, **bonafideContext))

@user_passes_test(lambda u: u.is_superuser)
def printBonafide(request,id=None):
    instance = Bonafide.objects.get(id=id)
    context = {
            "text"  :instance.text,
            "date"  :date.today(),
            "id"    :id
    }
    instance.printed=True;
    instance.save();
    return render(request,"bonafidepage.html",context)

def is_warden(user):
    return False if not Warden.objects.filter(user=user) else True

def is_hostelsuperintendent(user):
     return False if not HostelSuperintendent.objects.filter(user=user) else True

@login_required
@user_passes_test(is_warden)
def warden(request):
    warden = Warden.objects.get(user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel__icontains=warden.hostel).order_by('approved', '-id')
    context = {
        'option':1,
        'warden': warden,
        'leaves': leaves,
    }
    postContext = {}
    if request.GET:
        name = request.GET.get('name')
        date = request.GET.get('date')
        leavesearch=[]
        for leave in leaves:
            if name.lower() in leave.student.name.lower():
                dt=str(leave.dateTimeStart.year)+'-'+str(leave.dateTimeStart.month).zfill(2)+'-'+str(leave.dateTimeStart.day).zfill(2)
                if date == "" or date in dt:
                    leavesearch.append(leave)
        postContext = {
            'leaves':leavesearch
        }
    return render(request, "warden.html", dict(context, **postContext))

@login_required
@user_passes_test(is_hostelsuperintendent)
def hostelsuperintendent(request):
    hostelsuperintendents = HostelSuperintendent.objects.filter(user=request.user)
    daypass = []
    for hostelsuperintendent in hostelsuperintendents:
        for hostel in hostelsuperintendent.hostel.split(','):
            daypass += DayPass.objects.filter(student__hostelps__hostel__icontains=hostel).order_by('approved', '-id')
    print(daypass)
    context = {
        'option':1,
        'hostelsuperintendent': hostelsuperintendent,
        'daypasss': daypass
    }
    return render(request, "hostelsuperintendent.html", context)

@login_required
@user_passes_test(is_warden)
def wardenleaveapprove(request, leave):
    leave = Leave.objects.get(id=leave)
    warden = Warden.objects.get(user=request.user)
    daypasss = DayPass.objects.filter(student__hostelps__hostel=warden.hostel).order_by('approved', '-id')[:50]
    leaves = Leave.objects.filter(student=leave.student)

    context = {
        'option': 2,
        'warden': warden,
        'leave': leave,
        'daypasss' : daypasss,
        'leaves': leaves,
        'student': leave.student
    }

    if request.POST:
        approved = request.POST.getlist('group1')
        print(approved)
        comment = request.POST.get('comment')
        mail_message={}
        if config.EMAIL_PROD:
            email_to = [leave.student.email]
        else:
            email_to = ["spammailashad@gmail.com"]
            email_to = [leave.student.email]
        mail_subject="Leave Status - "
        mail_message=leave.student.name+",\n"

        if '1' in approved:
            leave.approved=True
            leave.disapproved = False
            leave.inprocess = False
            leave.approvedBy = warden
            mail_subject=mail_subject + "Successful!"
            mail_message=mail_message+ "Success! Your leave application with leave id: " + str(leave.id) + " from " + leave.dateTimeStart.strftime('%d/%m/%Y') + " to "+leave.dateTimeEnd.strftime('%d/%m/%Y')+" has been approved."
        elif '2' in approved:
            leave.disapproved=True
            leave.approved = False
            leave.inprocess = False
            leave.approvedBy = warden
            mail_subject=mail_subject + "Unsuccessful!"
            mail_message=mail_message+"Unsuccessful! Your leave application with leave id: "+ str(leave.id) + " from " + leave.dateTimeStart.strftime('%d/%m/%Y') + " to "+leave.dateTimeEnd.strftime('%d/%m/%Y')+" has been disapproved."
        else:
            leave.inprocess = True
            leave.approved = False
            leave.disapproved = False
            leave.approvedBy = None

        leave.comment = comment
        if(leave.comment != ''):
            mail_message=mail_message+"\nComments: " + leave.comment
        send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)
        leave.save()
        return redirect('warden')

    return render(request, "warden.html", context)

@login_required
@user_passes_test(is_hostelsuperintendent)
def hostelsuperintendentdaypassapprove(request, daypass):
    daypass = DayPass.objects.get(id=daypass)
    hostelsuperintendent = HostelSuperintendent.objects.filter(hostel__icontains=daypass.student.hostelps.hostel)
    hostelsuperintendent = hostelsuperintendent[0]
    context = {
        'option': 2,
        'hostelsuperintendent': hostelsuperintendent,
        'daypasss': daypass,
    }
    if request.POST:
        approved = request.POST.getlist('group1')
        print(approved)
        comment = request.POST.get('comment')

        mail_message={}
        if config.EMAIL_PROD:
            email_to = [daypass.student.email]
        else:
            email_to = ["swdbitstest@gmail.com"]
        mail_subject="Daypass Status - "
        mail_message=daypass.student.name+",\n"

        if '1' in approved:
            daypass.approved=True
            daypass.disapproved = False
            daypass.inprocess = False
            daypass.approvedBy = hostelsuperintendent
            mail_subject=mail_subject + "Successful!"
            mail_message=mail_message+ "Success! Your Daypass application with id: " + str(daypass.id) + " on " + daypass.dateTime.strftime('%d/%m/%Y') + " has been approved."
        elif '2' in approved:
            daypass.disapproved=True
            daypass.approved = False
            daypass.inprocess = False
            daypass.approvedBy = hostelsuperintendent
            mail_subject=mail_subject + "Unsuccessful!"
            mail_message=mail_message+ "Unsuccessful! Your Daypass application with id: " + str(daypass.id) + " on " + daypass.dateTime.strftime('%d/%m/%Y') + " has been disapproved."
        else:
            daypass.inprocess = True
            daypass.approved = False
            daypass.disapproved = False
            daypass.approvedBy = None

        daypass.comment = comment
        if(daypass.comment != ''):
            mail_message=mail_message+"\nComments: " + daypass.comment
        send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)
        daypass.save()
        return redirect('hostelsuperintendent')


    return render(request, "hostelsuperintendent.html", context)


@login_required
def daypass(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

        #dues
    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    form = DayPassForm()
    context = {
        'option1' : 0,
        'student': student,
        'form': form,
        'option': option,
        'mess': mess,
        'balance': balance,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
    }

    daypassContext = {
        'daypass': DayPass.objects.filter(student=student),
    }

    if request.POST:
        form = DayPassForm(request.POST)
        if form.is_valid():
            daypassform = form.save(commit=False)
            date1 = datetime.strptime(request.POST.get('date'), '%d %B, %Y').date()
            time = datetime.strptime(request.POST.get('time'), '%H:%M').time()
            intime = datetime.strptime(request.POST.get('intime'), '%H:%M').time()
            dateTime = datetime.combine(date1, time)
            inTime = datetime.combine(date1,intime)
            daypassform.dateTime = make_aware(dateTime)
            daypassform.student = student
            daypassform.inTime = make_aware(inTime)
            daypassform.save()

            if config.EMAIL_PROD:
                email_to=[HostelSuperintendent.objects.get(hostel__icontains=HostelPS.objects.get(student=student).hostel).email]
            else:
                email_to=["swdbitstest@gmail.com"]
                #print("hello")
                #print(HostelSuperintendent.objects.get(hostel__icontains=HostelPS.objects.get(student=student).hostel).email)
                                                                                   # For testing
            mailObj=DayPass.objects.latest('id')
            mail_subject="New Daypass ID: "+ str(mailObj.id)
            mail_message="Daypass Application applied by "+ mailObj.student.name +" with id: " + str(mailObj.id) + ".\n"
            #send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)

            context = {
                'option1': 1,
                'date': request.POST.get('date'),

            }
        else:
            context = {
                'option1': 2,
                'form': form
            }
            print(form.errors)
    return render(request, "daypass.html", dict(context, **daypassContext))

@user_passes_test(lambda u: u.is_superuser)
def messbill(request):
    # Exports Mess Bill dues in an excel file
    # template: messbill.html

    if request.GET:
        selected = request.GET['ids']
        values = [x for x in selected.split(',')]
    if request.POST:
        messOpt = request.POST.get('mess')
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+ str(messOpt) +'-MessBill.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet(str(messOpt) + "-Mess")

        heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
        h2_font_style = xlwt.easyxf('font: bold on')
        font_style = xlwt.easyxf('align: wrap on')

        # This function is not documented but given in examples of repo
        #     here: https://github.com/python-excel/xlwt/blob/master/examples/merged.py
        # Prototype:
        #     sheet.write_merge(row1, row2, col1, col2, 'text', fontStyle)
        ws.write_merge(0, 0, 0, 4, str(messOpt) + "-Mess", heading_style)

        start_date = datetime.strptime(request.POST.get('start_date'), '%d %B, %Y').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%d %B, %Y').date()
        end_date = end_date if end_date<date.today() else date.today()

        ws.write(1, 0, "From:", h2_font_style)
        ws.write(1, 1, start_date.strftime('%d/%b/%Y'), font_style)
        ws.write(1, 2, "To:", h2_font_style)
        ws.write(1, 3, end_date.strftime('%d/%b/%Y'), font_style)

        row_num = 2

        columns = [
            (u"Name", 6000),
            (u"ID", 6000),
            (u"Amount", 3000),
            (u"Rebate", 3000),
            (u"Final Amount", 3000),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], h2_font_style)
            ws.col(col_num).width = columns[col_num][1]

        with open(settings.CONSTANTS_LOCATION, 'r') as fp:
            data = json.load(fp)
        amount = float(data['mess-amount'])
        rebate = float(data['mess-rebate'])

        days = end_date - start_date
        days = days.days + 1

        values = MessOption.objects.filter(
            mess=messOpt,
            monthYear__range=(start_date.replace(day=1), end_date.replace(day=1))
        )

        for k in values:

            obj = k.student
            leaves = Leave.objects.filter(student=obj)
            # Count no of days for which rebate is given
            noofdays = 0
            # Count no of days for which full rebate is givem
            num_vac_days = 0

            for leave in leaves:
                if leave.approved == True:
                    if leave.dateTimeStart.date() >= start_date and leave.dateTimeStart.date() <= end_date and leave.dateTimeEnd.date() >= end_date:
                        length = abs(end_date -
                                        leave.dateTimeStart.date()).days + 1
                        if leave.comment == "Vacation":
                            num_vac_days += length
                        else:
                            noofdays += length
                    elif leave.dateTimeEnd.date() >= start_date and leave.dateTimeEnd.date() <= end_date and leave.dateTimeStart.date() <= start_date:
                        length = abs(leave.dateTimeEnd.date() -
                                        start_date).days + 1
                        if leave.comment == "Vacation":
                            num_vac_days += length
                        else:
                            noofdays += length
                    elif leave.dateTimeStart.date() >= start_date and leave.dateTimeEnd.date() <= end_date:
                        length = abs(leave.dateTimeEnd.date() -
                                        leave.dateTimeStart.date()).days + 1
                        if leave.comment == "Vacation":
                            num_vac_days += length
                        else:
                            noofdays += length
                    elif leave.dateTimeStart.date() <= start_date and leave.dateTimeEnd.date() >= end_date:
                        length = abs(end_date - start_date).days + 1
                        if leave.comment == "Vacation":
                            num_vac_days += length
                        else:
                            noofdays += length

            if request.POST.get('extype') is 'R':
                finalamt = amount * (days - num_vac_days) - rebate * noofdays

                row = [
                    obj.name,
                    obj.bitsId,
                    amount * days,
                    rebate * noofdays + amount * num_vac_days,
                    finalamt
                ]

                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

            elif request.POST.get('extype') is 'F':
                month_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))
                for month in month_list:
                    # The desc has to match with the desc in created Dues object
                    #       exactly same as desc created in import_mess_bill view
                    desc = "Mess Due " + month.strftime("%B %y")
                    dues = Due.objects.filter(student=obj, description=desc).first()
                    if dues is not None:
                        finalamt = dues.amount
                    else:
                        continue

                    row = [
                        obj.name,
                        obj.bitsId,
                        amount * days,
                        rebate * noofdays - amount * num_vac_days,
                        finalamt,
                        month.strftime("%B %y")
                    ]

                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
            else:
                messages.error(request, 'Invalid: extype={} found'.format(request.POST.get('extype')))

        wb.save(response)
        messages.success(request, "Export done. Download will automatically start.")
        return response

    return render(request, "messbill.html", {})

@user_passes_test(lambda u: u.is_superuser)
def import_mess_bill(request):
    # Template: import_mess_bill.html
    if request.POST:
        if request.FILES:
            xlfile_uploaded = request.FILES['newrebate']
            extension = xlfile_uploaded.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    return HttpResponse("Upload a Valid Excel (.xls or .xlsx) File")
            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xlfile_uploaded.read())
            workbook = xlrd.open_workbook(tmp)
            tot_dues_added = 0
            failed = ''
            year_selected = int(request.POST.get('year'))
            if year_selected == '':
                datetime.now().year
            for sheet in workbook.sheets():
                idx = 2
                try:
                    if (sheet.cell_value(2, 1) != 'ID') or (sheet.cell_value(2, 4) != 'Final Amount'):
                        os.remove(tmp)
                        return HttpResponse("Make sure the the sheet ({}) have proper header rows.".format(sheet.name))
                except IndexError:
                    os.remove(tmp)
                    return HttpResponse("Make sure the the sheet ({}) have proper header rows.".format(sheet.name))
                for col in sheet.get_rows():
                    idx += 1
                    # Skipping third row (for header)
                    # The last column(4) 'Final Amount' contains the dues
                    # Name | ID | Amount | Rebate | Final Amount
                    if idx > 2:
                        bitsId = col[1].value
                        try:
                            student = Student.objects.get(bitsId=bitsId)
                            due = float(col[4].value)
                            month = datetime.strptime(request.POST.get('month'), '%B').date()
                            month = month.replace(day=1, year=year_selected)
                            # desc is hardcoded and referenced in messbill view also
                            # any change here should also be done in desc
                            desc = "Mess Due " + month.strftime("%B %y")
                            category, created = DueCategory.objects.get_or_create(name='Mess Bill',
                                                       description=desc)
                            dues = Due.objects.create(student=student,
                                            amount=amount,
                                            due_category=category,
                                            description=desc,
                                            date_added=datetime.now())
                            tot_dues_added += 1
                        except Student.DoesNotExist:
                            failed += str(bitsId) + ', '
                        except IndexError:
                            os.remove(tmp)
                            return HttpResponse("Make sure the the sheet ({}) have proper header rows.".format(sheet.name))

            os.remove(tmp)
            if failed == '':
                failed = str(0)
            return HttpResponse(str(tot_dues_added) + " Dues successfully added.<br>" + failed + " bitsIDs not found in database")
        return HttpResponse("Upload file")
    return render(request, "import_mess_bill.html", {})



def store(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    tees = TeeAdd.objects.filter(available=True).order_by('-pk')
    items = ItemAdd.objects.filter(available=True)
    teesj = TeeAdd.objects.filter(available=True).values_list('title')

    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount
    balance = float(22000) - float(total_amount)

    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0



    # tees_json = json.dumps(list(tees), cls=DjangoJSONEncoder)
    context = {
        'student': student,
        'tees': tees,
        'items': items,
        'option': option,
        'balance': balance,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        # 'tees_json': tees_json,
    }

    if request.POST:
        if request.POST.get('what') == 'item':
            itemno = ItemAdd.objects.get(id=int(request.POST.get('info')))
            bought = False;
            if ItemBuy.objects.filter(student=student,item=itemno).exists():
                bought = True
            else:
                bought = False
            if bought == True:
                messages.add_message(request, messages.INFO,"You have already paid for "+ itemno.title,extra_tags='orange')
            elif itemno.available == True:
                itembuy = ItemBuy.objects.create(item = itemno, student=student)
                messages.add_message(request, messages.INFO, itemno.title + ' item bought. Thank you for purchasing. Headover to DUES to check your purchases.', extra_tags='green')
            else:
                messages.add_message(request, messages.INFO,  'Item not available', extra_tags='red')
        if request.POST.get('what') == 'tee':
            teeno = TeeAdd.objects.get(id=int(request.POST.get('info')))
            bought = False;
            query=TeeBuy.objects.filter(student=student,tee=teeno)
            try:
                nick = request.POST.get('nick')
                sizes = request.POST.get('sizes')
                colors = request.POST.get('colors')
                qty = request.POST.get('quantity')
                # Validation
                message_error = ""
                #if teeno.nick == True:
                #    if nick == "":
                #        message_error = "No nick provided. Please provide a nick."
                if teeno.sizes and sizes not in teeno.sizes.split(','):
                    message_error = "Size doesn't match the database."
                if teeno.colors and colors not in teeno.colors.split(','):
                    message_error = "Color doesn't match the database."
                if qty is None:
                    message_error = "Provide quantity of the tees you want."
                for i in range(0,query.count()):
                    if query[i].size==sizes:
                        bought = True
                if bought == True:
                    messages.add_message(request,messages.INFO,"You have already paid for "+ teeno.title,extra_tags='orange')
                elif message_error == "":
                    teebuy = TeeBuy.objects.create(tee = teeno, student=student, nick=nick, size=sizes, color=colors, qty=qty)
                    messages.add_message(request, messages.INFO, teeno.title + ' tee bought. Thank you for purchasing. Headover to DUES to check your purchases.', extra_tags='green')
                else:
                    messages.add_message(request, messages.INFO,  message_error, extra_tags='red')

            except Exception as e:
                print(e)
                print("Failed")
            # teebuy = TeeBuy.objects.create(tee = teeno, student=student, )
    return render(request, "store.html", context)

@login_required
def dues(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))

    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
    if messopen:
        messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

    if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
        option = 0
        mess = 0
    elif messopen and messoption:
        option = 1
        mess = messoption[0]
    else:
        option = 2
        mess = 0

    try:
        lasted = DuesPublished.objects.latest('date_published').date_published
    except:
        lasted = datetime(year=2004, month=1, day=1) # Before college was founded

    otherdues = Due.objects.filter(student=student)
    itemdues = ItemBuy.objects.filter(student=student,
                                      created__gte=lasted)
    teedues = TeeBuy.objects.filter(student=student,
                                      created__gte=lasted)
    total_amount = 0
    for item in itemdues:
        if item is not None:
            total_amount += item.item.price
    for tee in teedues:
        if tee is not None:
            total_amount += tee.totamt
    for other in otherdues:
        if other is not None:
            total_amount += other.amount            

    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    swd_adv = float(data['swd-advance'])
    balance = swd_adv - float(total_amount)
    balance = float(22000) - float(total_amount)

    context = {
        'student': student,
        'itemdues': itemdues,
        'teedues': teedues,
        'balance': balance,
        'otherdues': otherdues,
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
    }

    return render(request, "dues.html", context)

@login_required
def search(request):    
    perm=0;
    option='indexbase.html';
    context = {
        'hostels' : [i[0] for i in HOSTELS],
        'branches' : BRANCH,
        'permission': perm,
        'option' :option
    }
    
    if is_warden(request.user):
        warden = Warden.objects.get(user=request.user)
        option = 'wardenbase.html'
        perm=1
        context = {
            'hostels' : [i[0] for i in HOSTELS],
            'branches' : BRANCH,
            'permission': perm,
            'option' :option,
            'warden' : warden,
        }
    elif is_hostelsuperintendent(request.user):
        option = 'superintendentbase.html'
        perm=1
        hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
        context = {
            'hostels' : [i[0] for i in HOSTELS],
            'branches' : BRANCH,
            'permission': perm,
            'option' :option,
            'hostelsuperintendent':hostelsuperintendent,
        }
    elif request.user.is_superuser:
        perm=1
        context = {
            'hostels' : [i[0] for i in HOSTELS],
            'branches' : BRANCH,
            'permission': perm,
            'option' :option,
        }
    elif request.user.is_authenticated:
        student = Student.objects.get(user=request.user)
        leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
        daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
        bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))

        #mess
        messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
        messopen = messopen.exclude(dateOpen__gt=date.today())
        if messopen:
            messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

        if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
            option = 0
            mess = 0
        elif messopen and messoption:
            option = 1
            mess = messoption[0]
        else:
            option = 2
            mess = 0

        try:
            lasted = DuesPublished.objects.latest('date_published').date_published
        except:
            lasted = datetime(year=2004, month=1, day=1) # Before college was founded

        otherdues = Due.objects.filter(student=student)
        itemdues = ItemBuy.objects.filter(student=student,
                                        created__gte=lasted)
        teedues = TeeBuy.objects.filter(student=student,
                                        created__gte=lasted)
        total_amount = 0
        for item in itemdues:
            if item is not None:
                total_amount += item.item.price
        for tee in teedues:
            if tee is not None:
                total_amount += tee.totamt
        for other in otherdues:
            if other is not None:
                total_amount += other.amount
        balance = float(22000) - float(total_amount)

        context = {
           'hostels' : [i[0] for i in HOSTELS],
           'branches' : BRANCH,
           'permission': perm,
           'option' :option,
           'student' :student ,
           'leaves': leaves,
           'option': option,
           'mess': mess,
           'bonafides': bonafides,
           'daypasss': daypasss,
           'balance': balance
        }

      
    postContext = {}
    if request.GET:
        name = request.GET.get('name')
        bitsId = request.GET.get('bitsId')
        branch = request.GET.get('branch')
        hostel = request.GET.get('hostel')
        room = request.GET.get('room')

        students = Student.objects.filter(Q(name__icontains=name) & Q(bitsId__icontains=bitsId) & Q(bitsId__contains=branch) & Q(hostelps__hostel__contains=hostel) & Q(hostelps__room__contains=room))

        searchstr = {}

        if name is not "":
            searchstr['Name'] = name
        if bitsId is not "":
            searchstr['BITS ID'] = bitsId
        if branch is not "":
            searchstr['Branch'] = branch
        if hostel is not "":
            searchstr['Hostel'] = hostel
        if room is not "":
            searchstr['Room'] = room

        postContext = {
            'students' : students,
            'searchstr' : searchstr
        }
    
    if request.user.is_authenticated and not is_warden(request.user) and not is_hostelsuperintendent(request.user):
        return render(request, "search_logged_in.html", dict(context, **postContext))
    else:
        return render(request, "search.html", dict(context, **postContext))

def search_no_login(request):
    context = {
        'hostels' : [i[0] for i in HOSTELS],
        'branches' : BRANCH,
        'option': 'indexbase.html'
    }
    postContext = {}
    if request.GET:
        name = request.GET.get('name')
        bitsId = request.GET.get('bitsId')
        branch = request.GET.get('branch')
        hostel = request.GET.get('hostel')
        room = request.GET.get('room')

        students = Student.objects.filter(Q(name__icontains=name) & Q(bitsId__contains=bitsId) & Q(bitsId__contains=branch) & Q(hostelps__hostel__contains=hostel) & Q(hostelps__room__contains=room))

        searchstr = {}

        if name is not "":
            searchstr['Name'] = name
        if bitsId is not "":
            searchstr['BITS ID'] = bitsId
        if branch is not "":
            searchstr['Branch'] = branch
        if hostel is not "":
            searchstr['Hostel'] = hostel
        if room is not "":
            searchstr['Room'] = room
            
        postContext = {
            'students' : students,
            'searchstr' : searchstr
        }
    return render(request, "search.html", dict(context, **postContext))

def notice(request):
    context = {
        'queryset' : Notice.objects.all().order_by('-id')
    }
    return render(request,"notice.html",context)

def antiragging(request):
    return render(request,"antiragging.html",{})

def swd(request):
    return render(request,"swd.html",{})

def csa(request):
    y=1-(datetime.now().month-1)//6

    context = {
        'csa' : CSA.objects.all().order_by('priority'),
        'year' : datetime.now().year - y
    }
    return render(request,"csa.html",context)

def sac(request):
    return render(request,"sac.html",{})
    
def contact(request):
    context = {
        'warden' : Warden.objects.all() 
    }
    return render(request,"contact.html",context)

def studentDetails(request,id=None):
    if request.user.is_authenticated:
        if is_warden(request.user) or is_hostelsuperintendent(request.user) or request.user.is_superuser:
            student = Student.objects.get(id=id)
            res=HostelPS.objects.get(student__id=id)
            disco=Disco.objects.filter(student__id=id)
            context = {
                     'student'  :student,
                     'residence' :res,
                     'disco' : disco,
            }
            return render(request,"studentdetails.html",context)
        else:
            messages.error(request, "Unauthorised access. Contact Admin.")
            return render(request, "home1.html", {})            
    else:
        messages.error(request, "Login to gain access.")
        return redirect('login')
#        context = {
#        'queryset' : Notice.objects.all().order_by('-id')
#        }
#        return render(request, 'home1.html',context)


@login_required
def documents(request):
    if request.user.is_authenticated:
        if is_warden(request.user):
            warden = Warden.objects.get(user=request.user)
            context = {
                            'option1' : 'wardenbase.html',
                            'warden' : warden,
                            'queryset' : Document.objects.all().order_by('-pk'),
            }
        elif is_hostelsuperintendent(request.user):
            hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
            context = {
                            'option1' : 'superintendentbase.html',
                            'hostelsuperintendent' : hostelsuperintendent,
                            'queryset' : Document.objects.all().order_by('-pk'),
            }
        else:
            student = Student.objects.get(user=request.user)
            leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
            daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
            bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))

            #dues
            try:
                lasted = DuesPublished.objects.latest('date_published').date_published
            except:
                lasted = datetime(year=2004, month=1, day=1) # Before college was founded

            otherdues = Due.objects.filter(student=student)
            itemdues = ItemBuy.objects.filter(student=student,
                                              created__gte=lasted)
            teedues = TeeBuy.objects.filter(student=student,
                                              created__gte=lasted)
            total_amount = 0
            for item in itemdues:
                if item is not None:
                    total_amount += item.item.price
            for tee in teedues:
                if tee is not None:
                    total_amount += tee.totamt
            for other in otherdues:
                if other is not None:
                    total_amount += other.amount
            balance = float(22000) - float(total_amount)
            #mess
            messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
            messopen = messopen.exclude(dateOpen__gt=date.today())
            if messopen:
                messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

            if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
                option = 0
                mess = 0
            elif messopen and messoption:
                option = 1
                mess = messoption[0]
            else:
                option = 2
                mess = 0
            context = {
                            'option1' : 'base.html',
                            'student' : student,
                            'queryset' : Document.objects.all().order_by('-pk'),
                            'option': option,
                            'mess': mess,
                            'balance': balance,
                            'leaves': leaves,
                            'bonafides': bonafides,
                            'daypasss': daypasss,
            }
    return render(request,"documents.html",context)

def latecomer(request):
    if request.user.is_authenticated:
        finallist=[]
        late = LateComer.objects.all() 
        if is_warden(request.user):
            option = 'wardenbase.html'
            warden = Warden.objects.get(user=request.user)
            queryset = HostelPS.objects.filter(hostel__icontains=warden.hostel)
            for q in queryset:
                for instance in late:
                    if q.student == instance.student:
                        finallist.append(instance)
            context={
                        'warden' : warden,
                        'option' : option,
                        'list' : finallist,
            }
        elif is_hostelsuperintendent(request.user):
            finallist=late.order_by('-dateTime')
            option = 'superintendentbase.html'
            hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
            context={
                        'hostelsuperintendent' : hostelsuperintendent,
                        'option' : option,
                        'list' : finallist,
            }
        else:
            messages.error(request, "Unauthorised access. Contact Admin.")
            return render(request, "home1.html", {})
        return render(request,"latecomer.html",context)
    else:
        messages.error(request, "Login to gain access")
        return redirect('login')

def antiragging(request):
    context = {
                    'queryset' : AntiRagging.objects.all()
    }
    return render(request,"antiragging.html",context)



@user_passes_test(lambda u: u.is_superuser)
def mess_import(request):

    no_of_mess_option_added = 0
    if request.POST:
        if request.FILES:
            mess_file = request.FILES['file']

            import tempfile
            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(mess_file.read())
            workbook = xlrd.open_workbook(tmp)

            idx = 1


            for sheet in workbook.sheets():
                for i in sheet.get_rows():
                    if str(i[1].value)=="ID":
                        continue
                    # Format : Name | Bits ID | MESS
                    bid = str(i[1].value)
                    s = Student.objects.get(bitsId=bid)
                    month = date.today().month +1
                    my = datetime(date.today().year, month, 1)
                    messop = MessOption.objects.create(student = s, monthYear = my, mess = str(i[2].value))
                    no_of_mess_option_added += 1

    context = {'added': no_of_mess_option_added}
    return render(request, "mess_defaulters_upload.html", context)

@user_passes_test(lambda u: u.is_superuser)
def mess_exp(request):

    if request.POST:
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))

        gt_month = 0

        if month == 12:
            gt_month = 1
            gt_year = year+1
        else:
            gt_month = month + 1
            gt_year = year

        messopted = MessOption.objects.filter(monthYear__gte=datetime(year, month, 1), monthYear__lt=datetime(gt_year, gt_month,1))
        ids = []
        for i in range(len(messopted)):
            ids.append(messopted[i].student.bitsId)
        grad_ps = HostelPS.objects.filter(Q(status__exact="Graduate") | Q(status__exact="PS2"))
        for i in range(len(grad_ps)):
            ids.append(grad_ps[i].student.bitsId)


        students = Student.objects.exclude(bitsId__in=ids)



        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mess_defaulters.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Mess Defaulters')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Name', 'ID', 'Mess Alloted']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        s_list = students.values_list('name', 'bitsId')
        for s in s_list:
            row_num += 1
            for col_num in range(len(s)):
                ws.write(row_num, col_num, s[col_num], font_style)

        wb.save(response)
        return response

    years = [x for x in range(date.today().year-4, date.today().year+4,1)]
    months = [x for x in range(1,13,1)]
    context = { 'years': years,
                'months': months,
                }

    return render(request, "mess_export.html", context)


@user_passes_test(lambda a: a.is_superuser)
def dues_dashboard(request):
    return render(request, "dues_dashboard.html")

def retrieve_or_create_due_category(name, desc=""):
    query, created = DueCategory.objects.get_or_create(name=name,
                                                       description=desc)

    return query

@user_passes_test(lambda a: a.is_superuser)
def import_dues_from_sheet(request):
    if request.POST:
        if request.FILES:
            xlfile_uploaded = request.FILES['dues_sheet']
            extension = xlfile_uploaded.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    return redirect('dues_dashboard')

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xlfile_uploaded.read())
            workbook = xlrd.open_workbook(tmp)

            for sheet in workbook.sheets():
                first_iter = True
                categories = []
                for row in sheet.get_rows():
                    # ID No | Name | Expense 1 | Expense 2 | ... | Expense N
                    #              [ DueCategory(expense 1), DueCategory(expense 2), ...]
                    if first_iter:
                        for i in range(2, len(row)):
                            categories.append(retrieve_or_create_due_category(name=row[i].value))

                        first_iter = False
                        continue

                    try:
                        student = Student.objects.get(bitsId=row[0].value)
                    except Student.DoesNotExist:
                        messages.error(request,
                                "Student " + str(row[1].value) + " was not found in the database! SKIPPING HIS DUE ROW!")
                        continue

                    for i, category in enumerate(categories, start=2):
                        amount = float(row[i].value)

                        # Don't add the due if it's zero
                        if amount == 0: continue

                        # Check if the due already exists with same student
                        #   and same category, then overwrite that due object
                        #   instead of making new ones.

                        try:
                            # If there is a due with the same category name (i.e October Mess Bill '19, etc)
                            # we just overwrite it.
                            due = Due.objects.get(student=student,
                                                 due_category=category,
                                                 description=category.name)
                            due.amount = amount
                            due.save()
                        except Due.DoesNotExist as e:
                            Due.objects.create(student=student,
                                               amount=amount,
                                               due_category=category,
                                               description=category.name,
                                               date_added=datetime.now().date())

            os.remove(tmp)

            messages.success(request, "Dues have been imported")
        else:
            messages.error(request, "Please select a file to upload")
    else:
        messages.error(request, "Only POST requests are allowed")

    return redirect('dues_dashboard')

def developers(request):
    if request.user.is_authenticated:
            student = Student.objects.get(user=request.user)
            leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
            daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
            bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
            #dues
            try:
                lasted = DuesPublished.objects.latest('date_published').date_published
            except:
                lasted = datetime(year=2004, month=1, day=1) # Before college was founded

            otherdues = Due.objects.filter(student=student)
            itemdues = ItemBuy.objects.filter(student=student,
                                            created__gte=lasted)
            teedues = TeeBuy.objects.filter(student=student,
                                            created__gte=lasted)
            total_amount = 0
            for item in itemdues:
                if item is not None:
                    total_amount += item.item.price
            for tee in teedues:
                if tee is not None:
                    total_amount += tee.totamt
            for other in otherdues:
                if other is not None:
                    total_amount += other.amount
            balance = float(22000) - float(total_amount)

            #mess
            messopen = MessOptionOpen.objects.filter(dateClose__gte=date.today())
            messopen = messopen.exclude(dateOpen__gt=date.today())
            if messopen:
                messoption = MessOption.objects.filter(monthYear=messopen[0].monthYear, student=student)

            if messopen and not messoption and datetime.today().date() < messopen[0].dateClose:
                option = 0
                mess = 0
            elif messopen and messoption:
                option = 1
                mess = messoption[0]
            else:
                option = 2
                mess = 0

            context = {
                        'option1' : 'base.html',
                        'student': student,
                        'option': option,
                        'mess': mess,
                        'leaves': leaves,
                        'bonafides': bonafides,
                        'daypasss': daypasss,
                        'balance': balance,
            }
    else:
            context = {
                'option1' : 'indexbase.html',
        }

    return render(request, "developers.html", context)


@user_passes_test(lambda a: a.is_superuser)
def publish_dues(request):
    if request.POST:
        """
            Import entries from
            TeeBuy -> totamt, datetime added = created
            ItemBuy -> has foreign key to ItemAdd called item; use item.price,
                       datetime added = created

            Import only if the due above has creation datetime >
            last DuePublished timing
        """

        try:
            lasted = DuesPublished.objects.latest('date_published').date_published
        except:
            lasted = datetime(year=2004, month=1, day=1) # Before college was founded

        # Create/retrieve categories for
        # Tees, ItemBuy, LateComer
        tee_category = retrieve_or_create_due_category('TeeBuy', 'TShirt was bought')
        itembuy_category = retrieve_or_create_due_category('ItemBuy', 'An Item was bought')

        tees = TeeBuy.objects.filter(created__gte=lasted)
        for tee_buy in tees:
            due = Due(student=tee_buy.student,
                      amount=tee_buy.totamt,
                      due_category=tee_category,
                      description=tee_buy.tee.title,
                      date_added=tee_buy.created)
            due.save()

        itembuys = ItemBuy.objects.filter(created__gte=lasted)
        for itembuy in itembuys:
            due = Due(student=itembuy.student,
                      amount=itembuy.item.price,
                      due_category=itembuy_category,
                      description=itembuy.item.title,
                      date_added=itembuy.created)
            due.save()

        messages.success(request, "Dues have been published")
        DuesPublished.objects.create()
    else:
        messages.error(request, "Only POST requests are allowed")

    return redirect('dues_dashboard')


@user_passes_test(lambda a: a.is_superuser)
def edit_constants(request):
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    data_json = json.dumps(data)
    if request.POST:
        new_data = {}
        for element in data:
            new_data[element] = request.POST.get(element)
        with open(settings.CONSTANTS_LOCATION, 'w') as fw:
            json.dump(new_data, fw)
        messages.success(request, "constants.json updated")
    return render(request, "constants.html", {"initial": data_json})


def dash_security(request):
    from datetime import time
    t = time(0,0)
    t1 = time(23,59)
    d = date.today()
    #
    approved = Leave.objects.filter(approved__exact=True, dateTimeStart__gte=datetime.combine(d,t), dateTimeStart__lte=datetime.combine(d,t1))

    context = {'leaves' : approved}

    return render(request, "dash_security.html", context)

@user_passes_test(lambda u: u.is_superuser)

def import_cgpa(request):
    """
        Takes Excel Sheet as FILE input.
        Updates CGPA of the listed students in rows.
        The header row must contain 'studentID' and 'CGPA' as col names.
    """

    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "update_cgpa.html", {})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)
            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    try:
                        student = Student.objects.get(bitsId=row[header['studentID']].value)
                    except Student.DoesNotExist:
                        message_str = str(row[header['studentID']].value) + " not found in " \
                            "database"
                        messages.add_message(request,
                                            message_tag, 
                                            message_str)
                        print(message_str)
                        continue
                    change = student.change_cgpa(float(row[header['CGPA']].value))
                    if change is False:
                        message_str = str(row[header['studentID']].value) + " does not have " \
                            "a valid CGPA " + str(row[header['CGPA']].value)
                        messages.add_message(request,
                                            message_tag, 
                                            message_str)
                        print(message_str)
                    else:
                        print(str(row[header['studentID']].value) + " cgpa changed.")
                        count = count + 1
            message_str = "CGPAs successfully updated of " + str(count) + " students."
        else:
            message_str = "No File Added."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "update_cgpa.html", {})

@user_passes_test(lambda u: u.is_superuser)
def add_new_students(request):
    """
        Takes Excel Sheet as FILE input.
        Adds New Students to the database.
        The date fields expect a dd-Mon-yy value
        For example: 07-Jan-97
    """
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    
                    # create User model first then Student model
                    studentID = row[header['studentID']].value
                    if len(studentID)==13:
                        if studentID[4] == 'P':
                            username = 'p' + studentID[0:4] + studentID[8:12]
                        elif studentID[4] == 'H':
                            username = 'h' + studentID[0:4] + studentID[8:12]
                        else:
                            username = 'f' + studentID[0:4] + studentID[8:12]

                    else:
                        if studentID[4] == 'P':
                            username = 'p' + studentID[0:4] + studentID[8:11]
                        elif studentID[4] == 'H':
                            username = 'h' + studentID[0:4] + studentID[8:11]
                        else:
                            username = 'f' + studentID[0:4] + studentID[8:11]
                    print(username)
                    password = User.objects.make_random_password()

                    # Date of Birth and Date of Admit
                    # These col values are expected to be in dd-Mon-yy format
                    # For Example: 07-Jan-97
                    
                    try:
                        user = User.objects.get(username=username)
                        user.delete()
                    except User.DoesNotExist:
                        pass
                    user = User.objects.create_user(
                        username=username,
                        email='random@hello.com',
                        password=password)

                    # Date of Birth and Date of Admit
                    # These col values are expected to be in dd-Mon-yy format
                    # For Example: 07-Jan-97
                    dob = row[header['Stu_DOB']]
                    
                    if dob.ctype == 1: # XL_CELL_TEXT
                        rev_bDay = datetime.strptime(dob.value, '%d-%b-%Y').strftime('%Y-%m-%d')
                        
                    elif (dob.ctype == 3): # XL_CELL_DATE
                        rev_bDay = xlrd.xldate.xldate_as_datetime(dob.value, 0)
                        
                    else:
                        rev_bDay = datetime.strptime('01Jan1985', '%d%b%Y')
                        
                    
                    do_admit = row[header['admit']]
                    
                    if (do_admit.ctype == 1): # XL_CELL_TEXT
                        
                        rev_admit = datetime.strptime(do_admit.value, '%d/%m/%Y').strftime('%Y-%m-%d')
                        
                    elif do_admit.ctype == 3: # XL_CELL_DATE
                        rev_admit = xlrd.xldate.xldate_as_datetime(do_admit.value, 0)
                        
                    else:
                        rev_admit = datetime.strptime('01Jan1985', '%d%b%Y')

                    try:    
                        student = Student.objects.create(
                            user=user,
                            bitsId=str(row[header['studentID']].value)[:15],
                            name=str(row[header['name']].value)[:50],
                            bDay=rev_bDay,
                            admit=rev_admit,
                            gender=str(row[header['Stu_gender']].value)[0],
                            phone=str(row[header['stu_mobile']].value)[:15],
                            email=str(row[header['stu_email (other then institute)']].value),
                            address=str(row[header['ADDRESS']].value),
                            bloodGroup=str(row[header['bloodgp']].value)[:10],
                            parentName=str(row[header['fname']].value)[:50],
                            parentPhone=str(row[header['parent mobno']].value)[:20],
                            parentEmail=str(row[header['parent mail']].value)[:50]
                        )
                        count = count + 1
                    except Exception:
                        message_str + studentID + " failed"
                            
            message_str = str(count) + " new students added."
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Add Newly Admitted Students to Database"})

@user_passes_test(lambda u: u.is_superuser)
def add_wardens(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Add new wardens"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    emailID = row[header['Email:@goa.bits-pilani.ac.in']].value + "@goa.bits-pilani.ac.in"
                    username = emailID.split('@', 1)[0]
                    password = User.objects.make_random_password()
                    try:
                        user = User.objects.get(username=username)
                        user.delete()
                    except User.DoesNotExist:
                        pass
                    user = User.objects.create_user(
                        username=username,
                        email=emailID,
                        password=password)

                    
                    warden = Warden.objects.create(
                        user=user,
                        name=row[header['Name']].value,
                        phone_off=str(int(row[header['Tel:(Off.)']].value)),
                        phone_res=str(int(row[header['Tel:(Res.)']].value)),
                        email=emailID,
                        chamber=row[header['Chamber No.']].value,
                        hostel=row[header['Function']].value,
                        )
                    count = count + 1
            message_str = str(count) + " new wardens added."
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Add new wardens"})

@user_passes_test(lambda u: u.is_superuser)
def add_superintendents(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Add new superintendents"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    
                    emailID = row[header['Email:@goa.bits-pilani.ac.in']].value + "@goa.bits-pilani.ac.in"
                    username = emailID.split('@', 1)[0]
                    password = User.objects.make_random_password()
                    try:
                        user = User.objects.get(username=username)
                        user.delete()
                    except User.DoesNotExist:
                        pass
                    user = User.objects.create_user(
                        username=username,
                        email=emailID,
                        password=password)

                    
                    si = HostelSuperintendent.objects.create(
                        user=user,
                        name=row[header['Name']].value,
                        hostel=row[header['Hostels']].value,
                        chamber = row[header['Chamber No.']].value,
                        phone_off=row[header['Tel:(Off.)']].value,
                        phone_res=row[header['Tel:(Res.)']].value,
                        email=emailID,
                        )
                    count = count + 1
            message_str = str(count) + " new superintendents added."
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Add new superintendents"})

@user_passes_test(lambda u: u.is_superuser)
def update_hostel(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Hostel"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        student = Student.objects.filter(bitsId=row[header['studentID']].value)[:1]
                        #print(student)
                    except Student.DoesNotExist:
                        message_str = row[header['studentID']].value + " does not exist in database \n"
                        if message_str is not '':
                            messages.add_message(request,
                            message_tag, 
                            message_str)
                        continue
                    try:
                        hostel = HostelPS.objects.get(student=student)
                        new_hostel = row[header['Hostel']].value
                        if new_hostel == 'Graduate' or new_hostel == 'Faculty' or new_hostel == 'Part Time' or new_hostel == 'Permanent Withdrawal' or new_hostel == 'Temporary Withdrawal' or new_hostel == 'Registration Cancelled' or new_hostel == 'Withdrawal':
                            hostel.acadstudent=False
                            hostel.status = new_hostel
                        else:
                            hostel.acadstudent=True
                            hostel.status = "Student"
                        hostel.hostel = new_hostel
                        if row[header['Room']].value:
                            try:
                                hostel.room = str(int(row[header['Room']].value))
                            except Exception:
                                hostel.room = str(row[header['Room']].value)
                        else:
                            hostel.room = ''
                        hostel.psStation = ""
                        
                        hostel.save()
                        count = count + 1
                    except HostelPS.DoesNotExist:
                        HostelPS.objects.create(student=student, hostel=row[header['Hostel']].value, room=str(row[header['Room']].value), acadstudent=True, status="Student", psStation="")
                        count = count + 1
                    if message_str is not '':
                        messages.add_message(request,
                            message_tag, 
                            message_str)
            message_str = str(count) + " Updated students' hostel"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Hostel"})

@user_passes_test(lambda u: u.is_superuser)
def update_contact(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Hostel"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    
                    Student.objects.filter(
                        bitsId=row[header['studentID']].value
                        ).update(phone=str(row[header['Phone']].value)[:15])

                    
                    count = count + 1
            message_str = str(count) + " Updated students' contact"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Contact"})

@user_passes_test(lambda u: u.is_superuser)
def update_parent_contact(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Parent Contact"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        Student.objects.filter(
                            bitsId=row[header['studentID']].value
                            ).update(parentPhone=str(row[header['Parent Phone']].value)[:15])
                        count = count + 1
                    except Exception:
                        message_str + "Error in student: " + str(row[header['studentID']].value) + "\n"
                    
                    
            message_str = str(count) + " Updated students' contact"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Contact"})

@user_passes_test(lambda u: u.is_superuser)
def upload_latecomer(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Parent Contact"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    
                    try:
                        bitsId = row[header['studentID']].value
                        if not bitsId.endswith("G"):
                            bitsId = bitsId + "G"
                        s = Student.objects.filter(bitsId=bitsId).last()
                        if s is not None:
                            excel_date = row[header['date']].value
                            d = datetime(*xlrd.xldate_as_tuple(excel_date, 0))
                            LateComer.objects.create(
                                student = s,
                                dateTime = d
                                )
                            count = count + 1
                        else:
                            message_str = message_str + "ID number: " + row[header['studentID']].value+ " does not exist\n"
                            messages.add_message(request,
                                message_tag, 
                                message_str)
                    except IntegrityError:
                        message_str + "ID number: " + row[header['studentID']].value+ " does not exist\n"
                        
                message_str = str(count) + " Latecomers added"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Upload latecomers"})

@user_passes_test(lambda u: u.is_superuser)
def upload_disco(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Add new superintendent"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        s = Student.objects.filter(bitsId = row[header['studentID']].value).last()
                        if s is not None:
                            if row[header['dov']].value: 
                                excel_date = row[header['dov']].value
                                dov = datetime(*xlrd.xldate_as_tuple(excel_date, 0))
                            else:
                                dov = datetime.strptime('2004-01-01', '%Y-%m-%d')
                            disco = Disco.objects.create(
                            student = s,
                            dateOfViolation = dov,
                            subject = str(row[header['case']].value),
                            action = str(row[header['action']].value),
                            )
                            count = count + 1
                        else:
                            message_str = message_str + "ID number: " + row[header['studentID']].value+ " does not exist\n"
                            messages.add_message(request,
                            message_tag, 
                            message_str)   
                    except Exception:
                        message_str + "ID number: " + row[header['studentID']].value+ " does not exist\n"
                    
            message_str = str(count) + " Discos added"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Upload disco"})

@user_passes_test(lambda u: u.is_superuser)
def update_ids(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update ID numbers"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        Student.objects.filter(
                            bitsId=row[header['Old IDS']].value
                            ).update(bitsId=str(row[header['New IDS']].value)[:15])
                        count = count + 1
                    except Exception:
                        message_str + "Error in student: " + str(row[header['Old IDS']].value) + "\n"
                    
                    
            message_str = str(count) + " Updated IDS"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update IDs"})

@user_passes_test(lambda u: u.is_superuser)
def update_ps(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update PS/Thesis"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        student = Student.objects.filter(bitsId=row[header['studentID']].value)
                    except Exception:
                        message_str + "student " + row[header['studentID']].value + " not in database"
                    try:
                        hostel = HostelPS.objects.filter(student=student[0]).update(hostel=None, room=None, acadstudent=False, status=row[header['Status']].value, psStation=row[header['PS Station']].value)
                        count = count + 1
                    except Exception:
                        message_str + "update failed for " + studentID
                    
            message_str = str(count) + " Updated PS/Thesis"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update PS/Thesis"})


@user_passes_test(lambda u: u.is_superuser)
def export_mess_leave(request):
    if request.POST:
        month = int(request.POST["month"])
        year = int(request.POST["year"])
        mess = request.POST["mess"]

        _, month_end_day = monthrange(year, month)
        month_start_date = make_aware(datetime(year=year, month=month, day=1))
        month_end_date = make_aware(datetime(year=year, month=month, day=month_end_day))

        leave_within_month = \
            Q(dateTimeStart__month__exact=month, dateTimeStart__year__exact=year) |\
            Q(dateTimeEnd__month__exact=month, dateTimeEnd__year__exact=year)

        leaves = Leave.objects.filter(leave_within_month,          # Leave is in that month
            student__messoption__monthYear__month__exact=month,    # Was in that mess that month
            student__messoption__monthYear__year__exact=year,
            student__messoption__mess__exact=mess,
            approved__exact=True)

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="mess_leaves.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Mess Leave Details')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['ID', 'Name', 'Leave Start', 'Leave End', 'Number of days to bill']

        for i, col_name in enumerate(columns):
            ws.write(0, i, col_name, font_style)

        font_style = xlwt.XFStyle()
        for row_num, leave in enumerate(leaves, start=1):
            bill_start = max(leave.dateTimeStart, month_start_date)
            bill_end = min(leave.dateTimeEnd, month_end_date)
            num_days = (bill_end - bill_start).days + 1

            row_contents = [leave.student.bitsId, leave.student.name,
                leave.dateTimeStart, leave.dateTimeEnd, num_days]

            for col_num, content in enumerate(row_contents):
                ws.write(row_num, col_num, str(content), font_style)

        wb.save(response)
        return response

    return render(request, "export_mess_leave.html")

@user_passes_test(lambda u: u.is_superuser)
def update_address(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Address"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        student = Student.objects.get(bitsId=row[header['studentID']].value)
                        student.address = row[header['address']].value
                        student.save()
                    except Exception:
                        message_str + "student " + row[header['studentID']].value + " not in database"
                    
            message_str = str(count) + " Updated Address"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Address"})

@user_passes_test(lambda u: u.is_superuser)
def update_bank_account(request):
    message_str = ''
    message_tag = messages.INFO
    if request.POST:
        if request.FILES:
            # Read Excel File into a temp file
            xl_file = request.FILES['xl_file']
            extension = xl_file.name.rsplit('.', 1)[1]
            if ('xls' != extension):
                if ('xlsx' != extension):
                    messages.error(request, "Please upload .xls or .xlsx file only")
                    messages.add_message(request,
                                        message_tag, 
                                        message_str)
                    return render(request, "add_students.html", {'header': "Update Bank account number"})

            fd, tmp = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as out:
                out.write(xl_file.read())
            workbook = xlrd.open_workbook(tmp)

            count = 0
            idx = 1
            header = {}
            for sheet in workbook.sheets():
                for row in sheet.get_rows():
                    if idx == 1:
                        col_no = 0
                        for cell in row:
                            # Store the column names in dictionary
                            header[str(cell.value)] = col_no
                            col_no = col_no + 1
                        idx = 0
                        continue
                    # create User model first then Student model
                    try:
                        student = Student.objects.get(bitsId=row[header['studentID']].value)
                        student.bank_account_no = str(int(row[header['account']].value))
                        student.save()
                    except Exception:
                        message_str + "student " + row[header['studentID']].value + " not in database"
                    
            message_str = str(count) + " Updated Bank account"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Bank account"})


