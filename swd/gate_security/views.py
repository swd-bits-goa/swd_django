from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from main.models import Leave,DayPass
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
    found_leave = False
    found_daypass = False
    if request.POST:
        username = request.POST.get('username')        
        inout = InOut.objects.get(student__bitsId=username)
        place='chicalim'

        if inout:
            if inout.inCampus==True:
                inout.place=place
                inout.inCampus=False
                inout.outDateTime = datetime.now()
                inout.save()
            else:
                inout.place=place
                inout.inCampus=True
                inout.inDateTime = datetime.now()
                inout.save()

            try:
                daypass = DayPass.objects.get(approved=True, student__bitsId = username)
            except:
                daypass = None

            try:
                leave = Leave.objects.get(approved=True, student__bitsId = username)[-1]
                leavetime = datetime.strptime(leave.get('dateTimeStart'), '%d %B, %Y').date()
            except:
                leave = None
            

            if leave and leavetime > date.today():
                student = leave.student
                found_leave = True
                if '1' in 'activate1':
                    inout.onLeave = True
                    inout.save()
                    leave.inprocess = True
                    leave.save()
                context = {
                    'student': student,
                    'leave': leave,
                    'found_leave': found_leave
                }
            if daypass:
                student = daypass.student
                found_daypass = True
                if '2' in 'activate2':
                    inout.daypass = True
                    inout.save()
                context = {
                    'student': student,
                    'daypass': daypass,
                    'found_daypass': found_daypass,
                    'found_leave': found_leave
                }
            return render(request, "gate_security.html", context)

        else:
            #TO DO: error for invalid BITS ID using Django message framework
            pass

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

