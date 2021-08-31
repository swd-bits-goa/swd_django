from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib.auth.models import User
from main.templatetags.main_extras import is_hostelsuperintendent, is_warden, is_security, get_base_template
import swd.config as config
import datetime


# Create your views here.
# @user_passes_test(lambda u: u.is_superuser)
def gate_security(request):
    
    context = {}
    found_leave = False
    found_daypass = False
    if request.POST:
        username = request.POST.get('username')
        place = request.POST.get('place')
        
        inout = InOut.objects.filter(student__bitsId=username)

        if inout:
            if inout.inCampus==True:
                inout.place=place
                inout.inCampus=False
                inout.outDateTime = datetime.datetime.now()
                inout.inDateTime=null
                inout.save()
            else:
                inout.place=place
                inout.inCampus=True
                inout.inDateTime = datetime.datetime.now()
                inout.outDateTime=null
                inout.save()

            leave = Leave.objects.filter(approved=True, leave__student__bitsId = username)
            daypass = DayPass.objects.filter(approved=True, daypassses__student__bitsId = username)

            if leave:
                student = leave.student
                found_leave = True
                if '1' in 'activate1':
                    inout.onLeave = True
                    inout.save()
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

    return render(request, "gate_security.html", {'header': "Enter students coming in or going out of campus"},context)

# @user_passes_test(lambda u: u.is_superuser)
def in_out(request):

    inout = InOut.Objects.filter(inCampus = False)
    context = {
        'student': inout.student,
        'outtime': inout.outDateTime,
        'place': inout.place
    }

    return render(request, "all_in_out.html", {'header': "Check who all students are outside campus"},context)

