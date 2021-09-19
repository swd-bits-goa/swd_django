from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from main.models import Leave, DayPass, Student
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib.auth.models import User
from main.templatetags.main_extras import is_hostelsuperintendent, is_warden, is_security, get_base_template
import swd.config as config
from datetime import date, datetime, timedelta, time


# Create your views here.
# @user_passes_test(lambda u: u.is_superuser)
def gate_security(request):

    context = {}
    if request.method == 'POST':
        if request.POST.get("form_type") == 'formOne':
            username = request.POST.get('username')
            student = Student.objects.get(bitsId=username)
            inout = InOut.objects.get(student__bitsId=username)
            try:
                t = time(0,0)
                t1 = time(23,59)
                d = date.today()
                daypass = DayPass.objects.get(approved__exact=True, dateTime__date__exact=datetime.today().date(), student__bitsId = username)
            except:
                daypass = None

            try:
                t = time(0,0)
                t1 = time(23,59)
                d = date.today()
                leave = Leave.objects.get(dateTimeStart__gte=datetime.combine(d,t), dateTimeStart__lte=datetime.combine(d,t1), student__bitsId = username)
            except:
                leave = None

            context = {
                'student': student,
                'leave': leave,
                'daypass': daypass,
                'inout': inout,
            }
            return render(request, "gate_security.html", context)

        elif request.POST.get("form_type") == 'formTwo':
            username = request.POST.get('bitsid')
            student = Student.objects.get(bitsId=username)
            place = request.POST.get('place')
            leave_check = request.POST.get('leave_check')
            daypass_check = request.POST.get('daypass_check')

            inout = InOut.objects.get(student__bitsId=username)

            t = time(0,0)
            t1 = time(23,59)
            d = date.today()
            try:
                leave = Leave.objects.get(dateTimeStart__gte=datetime.combine(d,t), dateTimeStart__lte=datetime.combine(d,t1), student__bitsId = username)
            except:
                leave = None
            try:
                daypass = DayPass.objects.get(approved__exact=True, dateTime__date__exact=datetime.today().date(), student__bitsId = username)
            except:
                daypass = None
                
            if inout:
                if inout.inCampus==True:
                    inout.place=place
                    inout.inCampus=False
                    inout.outDateTime = datetime.now()
                    inout.inDateTime = None
                    inout.save()

                    if leave_check:
                        inout.onLeave = True
                        inout.save()
                        leave.inprocess = True
                        leave.save()

                    if daypass_check:
                        inout.daypass = True
                        inout.save()
                        leave.inprocess = True
                        leave.save()

                else:
                    inout.place=place
                    inout.inCampus=True
                    inout.inDateTime = datetime.now()
                    inout.outDateTime = None
                    if inout.onLeave == True:
                        inout.onLeave = False
                        leave.inprocess = False
                        leave.save()
                    if inout.onDaypass == True:
                        inout.onDaypass = False
                        daypass.inprocess = False
                        daypass.save()
                    inout.save()
            else:
                # inout = InOut(student=student, place=place, )
                pass

            context = {
                'student': student,
                'inout': inout,
                'success': True,
            }

            return render(request, "gate_security.html", context)

    return render(request, "gate_security.html", context)

# @user_passes_test(lambda u: u.is_superuser)
def in_out(request):

    inout = InOut.objects.filter(inCampus = False)
    context = {
        'inout': inout,
    }

    return render(request, "all_in_out.html",context)

@user_passes_test(is_security)
def dash_security_leaves(request):
    t = time(0,0)
    t1 = time(23,59)
    d = date.today()
    approved_leaves = Leave.objects.filter(approved__exact=True, dateTimeStart__gte=datetime.combine(d,t), dateTimeStart__lte=datetime.combine(d,t1))
    context = {'leaves' : approved_leaves}
    return render(request, "dash_security.html", context)


@user_passes_test(is_security)
def dash_security_daypass(request):
    t = time(0,0)
    t1 = time(23,59)
    d = date.today()
    approved_daypass = DayPass.objects.filter(approved__exact=True, dateTime__date__exact=datetime.today().date())
    context = {'daypasses' : approved_daypass}
    return render(request, "daypasses_security.html", context)

