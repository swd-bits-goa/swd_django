from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import InOut, WeekendPass
from main.models import Leave, DayPass, Student
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from main.templatetags.main_extras import is_hostelsuperintendent, is_warden, is_security, get_base_template
import swd.config as config
from datetime import date, datetime, timedelta, time


@user_passes_test(lambda u: u.is_superuser or is_security(u))
def gate_security(request):
    context = {}
    errors = []
    if request.method == 'POST':
        if request.POST.get("form_type") == 'formOne':
            username = request.POST.get('username')
            try:
                student = Student.objects.get(bitsId=username)
                errors = []
            except Student.DoesNotExist:
                student = None
                errors.append("Please enter correct BITS ID")

            try:
                inout = InOut.objects.get(student__bitsId=username)
            except InOut.DoesNotExist:
                inout = None

            try:
                daypass = DayPass.objects.get(
                        approved__exact=True,
                        dateTime__date__exact=datetime.today().date(),
                        student__bitsId=username,
                        claimed=False
                )
            except DayPass.DoesNotExist:
                daypass = None

            try:
                t = time(0,0)
                t1 = time(23,59)
                d = date.today()
                leave = Leave.objects.get(
                        dateTimeStart__gte=datetime.combine(d,t),
                        dateTimeStart__lte=datetime.combine(d,t1),
                        student__bitsId=username,
                        claimed=False
                )
            except Leave.DoesNotExist:
                leave = None
            
            try:
                weekendpass = WeekendPass.objects.get(
                        student__bitsId=username,
                        expiryDate__gte=datetime.today().date(),
                        approved=True)
            except WeekendPass.DoesNotExist:
                weekendpass = None

            context = {
                'student': student,
                'leave': leave,
                'daypass': daypass,
                'inout': inout,
                'errors': errors,
            }
            return render(request, "gate_security.html", context)

        elif request.POST.get("form_type") == 'formTwo':
            username = request.POST.get('bitsid')
            student = Student.objects.get(bitsId=username)
            place = request.POST.get('place')
            leave_check = request.POST.get('leave_check')
            daypass_check = request.POST.get('daypass_check')
            incampus_check = request.POST.get('incampus_check')
            weekendpass_check = request.POST.get('weekendpass_check')

            try:
                inout = InOut.objects.get(student__bitsId=username)
            except InOut.DoesNotExist:
                inout = None

            t = time(0,0)
            t1 = time(23,59)
            d = date.today()
            try:
                leave = Leave.objects.get(
                            (
                                Q(dateTimeStart__gte=datetime.combine(d,t)) &
                                Q(dateTimeStart__lte=datetime.combine(d,t1)) &
                                Q(claimed=False)
                            ) |
                            Q(inprocess=True),
                            student__bitsId=username
                )
            except Leave.DoesNotExist:
                leave = None

            try:
                daypass = DayPass.objects.get(
                        (
                            Q(approved__exact=True) &
                            Q(dateTime__date__exact=datetime.today().date()) &
                            Q(claimed=False)
                        ) |
                        Q(inprocess=True),
                        student__bitsId=username
                )
            except DayPass.DoesNotExist:
                daypass = None

            try:
                weekendpass = WeekendPass.objects.get(
                        student__bitsId=username,
                        expiryDate__gte=datetime.today().date(),
                        approved=True)
            except WeekendPass.DoesNotExist:
                weekendpass = None

            if inout:
                if inout.inCampus == True:
                    # Student is leaving campus
                    inout.place = place
                    inout.inCampus = False
                    inout.outDateTime = datetime.now()
                    inout.inDateTime = None
                    inout.save()

                    if leave_check:
                        inout.onLeave = True
                        inout.save()
                        leave.inprocess = True
                        leave.save()

                    elif daypass_check:
                        inout.onDaypass = True
                        inout.save()
                        daypass.inprocess = True
                        daypass.save()

                    elif weekendpass_check:
                        inout.onWeekendPass = True
                        inout.save()

                else:
                    inout.place = place
                    inout.inCampus = True
                    inout.inDateTime = datetime.now()
                    inout.outDateTime = None
                    if inout.onLeave == True:
                        leave.inprocess = False
                        leave.claimed = True
                        leave.save()
                    if inout.onDaypass == True:
                        daypass.inprocess = False
                        daypass.claimed = True
                        daypass.save()
                    inout.save()
            else:
                inout = InOut(
                            student=student,
                            place=place,
                            inDateTime=datetime.now(),
                            outDateTime=datetime.now(),
                            inCampus=False,
                            onLeave=False,
                            onDaypass=False
                )
                if not incampus_check:
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
                        inout.onDaypass = True
                        inout.save()
                        daypass.inprocess = True
                        daypass.save()

                else:
                    inout.place=place
                    inout.inCampus=True
                    inout.inDateTime = datetime.now()
                    inout.outDateTime = None
                    if inout.onLeave == True:
                        inout.onLeave = False
                        leave.inprocess = False
                        leave.claimed = True
                        leave.save()
                    if inout.onDaypass == True:
                        inout.onDaypass = False
                        daypass.inprocess = False
                        daypass.claimed = True
                        daypass.save()
                    inout.save()
            context = {
                'student': student,
                'inout': inout,
                'success': True,
            }
            return render(request, "gate_security.html", context)
    return render(request, "gate_security.html", context)


@user_passes_test(lambda u: u.is_superuser or is_security(u))
def dash_security_leaves(request):
    t = time(0,0)
    t1 = time(23,59)
    d = date.today()
    approved_leaves = Leave.objects.filter(approved__exact=True, dateTimeStart__gte=datetime.combine(d,t), dateTimeStart__lte=datetime.combine(d,t1)).order_by('-dateTimeStart')
    context = {'leaves' : approved_leaves}
    return render(request, "dash_security.html", context)


@user_passes_test(lambda u: u.is_superuser or is_security(u))
def dash_security_daypass(request):
    t = time(0,0)
    t1 = time(23,59)
    d = date.today()
    approved_daypass = DayPass.objects.filter(approved__exact=True, dateTime__date__exact=datetime.today().date()).order_by('-dateTime')
    context = {'daypasses' : approved_daypass}
    return render(request, "daypasses_security.html", context)

@user_passes_test(lambda u: u.is_superuser or is_security(u))
def in_out(request):
    inout = InOut.objects.filter(inCampus = False, onLeave = False, onDaypass = False).order_by('-outDateTime')
    context = {
        'inout': inout,
    }
    return render(request, "all_in_out.html",context)

@user_passes_test(lambda u: u.is_superuser or is_security(u))
def leave_out(request):
    inout = InOut.objects.filter(inCampus = False, onLeave = True, onDaypass = False).order_by('-outDateTime')
    context = {
        'inout': inout,
    }
    return render(request, "leave_out.html", context)

@user_passes_test(lambda u: u.is_superuser or is_security(u))
def daypass_out(request):
    inout = InOut.objects.filter(inCampus = False, onLeave = False, onDaypass = True).order_by('-outDateTime')
    context = {
        'inout': inout,
    }
    return render(request, "daypass_out.html", context)

@user_passes_test(lambda u: u.is_superuser or is_security(u))
def dash_security_weekendpass(request):
    approved_weekend = WeekendPass.objects.filter(
            approved=True,
            expiryDate__gte=datetime.today().date()
    )
    context = {'weekend_pass' : approved_weekend}
    return render(request, "weekend_security.html", context)
