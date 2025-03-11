from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.views.decorators.csrf import csrf_protect
from datetime import date, time, datetime, timedelta
from .forms import MessBillForm, MessForm, LeaveForm, BonafideForm, DayPassForm, VacationLeaveNoMessForm
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from main.storage import no_duplicate_storage
from tools.utils import gen_random_datetime


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.models import User

from calendar import monthrange, month_name
from dateutil import rrule
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Q
from .models import BRANCH, HOSTELS

from .templatetags.main_extras import is_hostelsuperintendent, is_warden, is_security, get_base_template

import swd.config as config

import re
import xlrd
xlrd.xlsx.ensure_elementtree_imported(False, None)
xlrd.xlsx.Element_has_iter = True
import xlwt
import os
import tempfile
import json

from calendar import monthrange

from pytz import timezone

@user_passes_test(lambda a: a.is_superuser)
def view_duplicates(request, end_year:str):
    """
    Shows duplicate students from year 2000 to the given end_year (default: current year)
    URL: admin/view_duplicates/<optional end_year>
    """
    students = []

    # If the end year isn't given, default to current year
    if end_year == None:
        end_year = datetime.now().year
    # Limit end_year to [2000, <current year>]
    end_year = max(2000, min(datetime.now().year, int(end_year)))

    years = [2000, int(end_year)+1]
    for year in range(*years):
        students.extend(Student.objects.filter(bitsId__startswith=str(year)))
    
    # students -> list of Student objects in the given range of years

    id_dict = {}
    duplicate_list = []
    nulls = []
    fields = ['admit', 'bDay']
    for idx, student in enumerate(students):
        # If student hasn't been seen before
        # Add to set of ids and continue
        if not student.bitsId in id_dict:
            id_dict[student.bitsId] = idx
            continue
    
        # At this point we know that `student` has been seen before

        s1 = student
        s2 = students[id_dict[student.bitsId]]

        # Identify which of s1 and s2 is the inferior duplicate
        inferior = None
        master = None
        for field in fields:
            f1 = getattr(s1, field)
            f2 = getattr(s2, field)
            if f1==None and f2==None: continue
            if f1!=None and f2!=None: continue
            if f1:
                master = s1 
                inferior = s2
                break
            master = s2
            inferior = s1
            break
        if inferior == None:
            # Contingency in case somehow both objects have all fields
            nulls.append(s1)
        else:
            duplicate_list.append([master, inferior])

    # duplicate_list -> list of [master object, inferior object] lists

    return render(request, "view_duplicates.html", {
        "students": duplicate_list,
        "start_year": 2000,
        "end_year": end_year,
    })

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
        if Security.objects.filter(user=request.user):
            return redirect('dash_security_leaves')
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

        sf = Staff.objects.all()

        context = {
            'sf' : sf,
            'queryset' : notices,
        }

        return render(request, 'home.html',context)


def login_success(request):
    return HttpResponse("Success!")

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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

    #mess
    messopen = MessOptionOpen.objects.filter(dateClose__gte=datetime.today())
    messopen = messopen.exclude(dateOpen__gt=date.today())
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
        'student': student,
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        'balance': balance,
        'address': address,
        'queryset' : notices,
        'tees': tees,
        'items': items
    }

    # Check for hostel documents
    hostel_documents = []
    hostelps = HostelPS.objects.filter(student=student).first()
    if hostelps:
        # Hostel found, now get documents with that hostel
        hostel_document_query = Q(hostels__contains=hostelps.hostel)
        hostel_documents = Document.objects.filter(hostel_document_query)
    if len(hostel_documents) != 0:
        context.update({
            'hostel_documents': hostel_documents,
            'hostelps': hostelps.hostel
        })

    return render(request, "dashboard.html", context)


@login_required
def profile(request):
    if is_warden(request.user):
        warden = Warden.objects.get(user=request.user)
        context = {
            'option1' : 'wardenbase.html',
            'warden' : warden,
        }
        return render(request, "profile.html", context)

    if is_hostelsuperintendent(request.user):
        hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
        context = {
            'option1' : 'superintendentbase.html',
            'hostelsuperintendent' : hostelsuperintendent
        }
        return render(request, "profile.html", context)

    # By this point, user is not a warden or superintendent

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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
        'hostelps': hostelps,
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
        if Security.objects.filter(user=request.user):
            return redirect('dash_security_leaves')
        return redirect('dashboard')

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username.lower(), password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin')
            if Warden.objects.filter(user=request.user):
                return redirect('/warden')
            if HostelSuperintendent.objects.filter(user=request.user):
                return redirect('/hostelsuperintendent')
            if Security.objects.filter(user=request.user):
                return redirect('dash_security_leaves')
            return redirect('dashboard')
        else:
            messages.add_message(request, messages.INFO,  "Incorrect username or password", extra_tags='red')

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

    # MessOptionOpen or None
    messopen_current = MessOptionOpen.objects.filter(dateClose__gte=date.today(), dateOpen__lte=date.today()).first() or None

    messoption = None # MessOption or None
    errors = []

    if messopen_current: # If there is a MessOptionOpen active right now
        # Get the student's MessOption
        messoption = MessOption.objects.filter(student=student, monthYear=messopen_current.monthYear).first()
    else:
        # Get the most recent MessOptionOpen
        messopen_last = MessOptionOpen.objects.all().last()
        messoption = None
        if messopen_last:
            # Get student's messoption from the most recent MessOptionOpen, otherwise set it to None
            messoption = MessOption.objects.filter(monthYear=messopen_last.monthYear, student=student).first()

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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

    edit = True if (request.GET and 'edit' in request.GET) else False
    
    context = {
        'student': student,
        'balance': balance,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
    }

    if messopen_current and (not messoption or edit):
        # If a MessOptionOpen is active and student doesn't have a MessOption / wants to edit it
        # Opens the edit page
        form = MessForm(request.POST)
        context.update({
            'option': 0,
            'mess': messopen_current,
            'form': form,
            'dateClose': messopen_current.dateClose,
        })
    elif messopen_current and messoption:
        # Messopen is active and student already has a MessOption
        # Page shows the MessOption and an edit button
        context.update({
            'option': 1,
            'mess': messoption,
        })
    elif messoption:
        # Messopen is not active and student already has a messoption
        # Page shows "you have filled this period's mess as <messname>"
        context.update({
            'option': 2,
            'mess': messoption,
        })
    else:
        # messoptionopen is not active and student doesn't have a messoption
        # Page shows "Nothing's Here, come back again please!"
        context.update({
            'option': 3,
        })
    
    vacations = VacationDatesFill.objects \
        .filter(dateClose__gte=date.today(), dateOpen__lte=date.today()) \
        .exclude(messOption=None)
    
    if vacations:
        vacation_open = vacations[0]
        student_vacation = Leave.objects.filter(
            student=student,
            reason=vacation_open.description
        )
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

        if (vacations.count() and len(errors) == 0) or (vacations.count() == 0) or (edit and len(errors) == 0):
            # Mess Option Filling
            mess = request.POST.get('mess')
            
            # At this point we know the user is trying to do something with the messoption
            # edit = True if there IS a current messoption, else False
            edit = True if (messopen_current and messoption and messoption.monthYear == messopen_current.monthYear) else False

            if messopen_current.get_capacity(mess) != None:
                if MessOption.objects.filter(monthYear=messopen_current.monthYear, mess=mess).count() < messopen_current.get_capacity(mess):
                    # Mess isn't full, so create the messoption
                    if edit:
                        messoption.student = student
                        messoption.monthYear = messopen_current.monthYear
                        messoption.mess = mess
                    else:
                        messoption = MessOption(
                            student = student,
                            monthYear = messopen_current.monthYear,
                            mess = mess
                        )
                    messoption.save()
                    context['mess'] = messoption
                    context['option'] = 1
                    # Redirect back to same page to avoid form resubmission popup
                    return redirect("messoption")
                else:
                    context['capacity']="Choose different mess, capacity full."
            else: # In case they gave no capacity, assume it is unlimited
                if edit:
                    messoption.student = student
                    messoption.monthYear = messopen_current.monthYear
                    messoption.mess = mess
                else:
                    messoption = MessOption(
                        student = student,
                        monthYear = messopen_current.monthYear,
                        mess = mess
                    )
                messoption.save()
                # Redirect back to same page to avoid form resubmission popup
                return redirect("messoption")

    return render(request, "mess.html", context)


@login_required
def vacation_no_mess(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
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

    # Dues
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
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

    form = VacationLeaveNoMessForm()
    vacations = VacationDatesFill.objects.filter(
        dateClose__gte=date.today(),
        dateOpen__lte=date.today(),
        messOption=None
    )
    vacation_context = {}

    if vacations:
        vacation_open = vacations[0]
        student_vacation = Leave.objects.filter(
                student=student,
                reason=vacation_open.description)
        if student_vacation.count():
            student_vacation = student_vacation[0]
        else:
            student_vacation = None
    else:
        vacation_open = None
        student_vacation = None
   
    vacation_context['vacation'] = vacation_open
    vacation_context['student_vacation'] = student_vacation
    
    context = {
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'balance' : balance,
        'daypasss': daypasss,
        'student': student
    }

    errors = []
    if vacation_open and student_vacation is None:
        if request.POST:
            form = VacationLeaveNoMessForm(request.POST)
            if form.is_valid():
                in_date = datetime.strptime(request.POST.get('in_date'), '%d %B, %Y').date()

                time0 = time.min
                out_date = datetime.strptime(request.POST.get('out_date'), '%d %B, %Y').date()
                in_date = datetime.combine(in_date, time0)
                out_date = datetime.combine(out_date, time0)

                allowed = True
                if not vacation_open.check_date_in_range(in_date):
                    errors.append("In Date should be within specified range.")
                    allowed = False
                if not vacation_open.check_date_in_range(out_date):
                    allowed = False
                    errors.append("Out Date should be within specified range.")
                if in_date < out_date:
                    allowed = False
                    errors.append("Out Date should be before In Date")
                if allowed:
                    created, obj = vacation_open.create_vacation(
                            student, out_date, in_date)
                    if not created:
                        errors.append(obj)
                    else:
                        vacation_context['student_vacation'] = obj
                
                if len(errors) == 0:
                    context['option1'] = 1
                else:
                    context['option1'] = 2
            else:
                context['option1'] = 2
        else:
            errors = []
            context['option1'] = 0
            if vacation_open and vacation_open.forceInDate == True:
                # If forceInDate is enabled, set in_date to the vacation in-date
                form.fields["in_date"].initial = vacation_open.allowDateBefore.strftime('%d %B, %Y')
    else:
        if vacation_open is None:
            context['option1'] = 1
            errors.append("No vacations nearby. Please keep checking this space for other details.")
        if student_vacation is not None:
            context['option1'] = 1
            errors.append("You have already submitted the details.")

    vacation_context['errors'] = errors
    context['form'] = form
    
    return render(
            request,
            "vacation_no_mess.html",
            dict(context, **vacation_context)
    )


@login_required
@noPhD
def leave(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    # mess
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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
            strdateTimeStart = dateTimeStart.strftime("%d/%m/%Y")
            dateEnd = datetime.strptime(request.POST.get('dateEnd'), '%d %B, %Y').date()
            timeEnd = datetime.strptime(request.POST.get('timeEnd'), '%H:%M').time()
            dateTimeEnd = datetime.combine(dateEnd, timeEnd)
            strdateTimeEnd = dateTimeEnd.strftime("%d/%m/%Y")
            leaveform.corrPhone = request.POST.get('phone_number')
            leaveform.dateTimeStart = make_aware(dateTimeStart)
            leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            leaveform.student = student
            if Leave.objects.filter(student=student,dateTimeStart=dateTimeStart,dateTimeEnd=dateTimeEnd).exists():
                pass
            else:
                leaveform.save()
                if config.EMAIL_PROD:
                    email_to=[Warden.objects.get(hostel=HostelPS.objects.get(student=student).hostel).email]
                    email_to_parent= [student.parentEmail]
                    # email_to_suprintendent = [HostelSuperintendent.objects.get(hostel=HostelPS.objects.get(student=student).hostel).email]
                else:
                    email_to=["div060916@gmail.com"]                                                                     # For testing
                    email_to_parent=["div060916@gmail.com"]
                mailObj = Leave.objects.latest('id')
                mail_subject = "New Leave ID: "+ str(mailObj.id)
                if mailObj.student.parentEmail is None:
                    messages.error(
                    request,
                    "Could not apply leave as parent's email was not found. "
                    "Please contact SWD to update the parent's email before applying for leave."
                     )
                    context = {
                    'option': option,
                    'mess': mess,
                    'leaves': leaves,
                    'bonafides': bonafides,
                    'balance': balance,
                    'daypasss': daypasss,
                    'option1': 2, 
                    'form': form,
                    'student': student
                        }
                    return render(request, "leave.html", dict(context, **leaveContext))
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
                    
                mail_message = "Leave Application applied by " + mailObj.student.name + " with leave id: " + str(mailObj.id) + ".\n"
                mail_message = mail_message + "Parent name: " + parentName + "\nParent Email: " + parentEmail + "\nParent Phone: " + parentPhone

                mail_message_to_parent = "Your ward has applied for the leave "+ mailObj.student.name + ".\n"
                mail_message_to_parent = mail_message_to_parent + "from " + strdateTimeStart + " to " + strdateTimeEnd + ".\n"
                mail_message_to_parent = mail_message_to_parent+ "The warden will approve the leave as per the eligibility" + ".\n"
                mail_message_to_parent = mail_message_to_parent+ "If you have any objection, kindly advise your ward accordingly or reach out to the warden at " + email_to[0] + ".\n"
                mail_message_to_parent = mail_message_to_parent+ "for cancellation of leave immediately." + "\n"
                mail_message_to_parent = mail_message_to_parent+ "You are strictly advised to reply to the respective Hostel warden mentioned in the mail " + email_to[0] + ".\n"
                mail_message_to_parent = mail_message_to_parent+ "Also, please make sure you mail to the warden only incase if you have an objection with the said leave"
                mail_message_to_parent = mail_message_to_parent+ "Regards," + "\n"
                mail_message_to_parent = mail_message_to_parent+ "SWD"

                mail_subject_to_parent = "Leave applied by " + mailObj.student.name


                send_mail(mail_subject, mail_message, settings.EMAIL_HOST_USER, email_to, fail_silently=False)

                #email to parent

                send_mail(mail_subject_to_parent, mail_message_to_parent, settings.EMAIL_HOST_USER, email_to_parent, fail_silently=False)

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
                    'student': student
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
                'form': form,
                'student': student
            }
    return render(request, "leave.html", dict(context, **leaveContext))


@login_required
@noPhD
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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
    queryset=Bonafide.objects.filter(student=student)
    rejected = 0
    for bonafide in queryset:
        if bonafide.status=="Rejected":
            rejected = 1
    bonafideContext = {
        'bonafides': queryset,
        'rejected': rejected
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

@user_passes_test(lambda u: u.is_staff)
def printBonafide(request,id=None):
    instance = Bonafide.objects.get(id=id)
    context = {
        "text": instance.text,
        "date": date.today(),
        "id": id
    }
    instance.printed=True
    instance.status='Approved'
    instance.save() 
    return render(request,"bonafidepage.html",context)


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
    hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
    daypass = DayPass.objects.all().order_by('-inprocess', '-dateTime')
    
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
        comment = request.POST.get('comment')
        mail_message={}
        if config.EMAIL_PROD:
            email_to = [str(leave.student.user.username) + "@goa.bits-pilani.ac.in"]
        else:
            email_to = ["spammailashad@gmail.com"]
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
    hostelsuperintendent = HostelSuperintendent.objects.get(user=request.user)
    context = {
        'option': 2,
        'hostelsuperintendent': hostelsuperintendent,
        'daypasss': daypass,
    }
    if request.POST:
        approved = request.POST.getlist('group1')
        comment = request.POST.get('comment')

        mail_message={}
        if config.EMAIL_PROD:
            email_to = [str(daypass.student.user.username) + "@goa.bits-pilani.ac.in"]
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
@noPhD
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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
        form = DayPassForm(request.POST, request.FILES)
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
            context = {
                'option1': 1,
                'date': request.POST.get('date'),
                'student': student
            }
        else:
            context = {
                'option1': 2,
                'form': form,
                'student': student,
            }
    return render(request, "daypass.html", dict(context, **daypassContext))

@user_passes_test(lambda u: u.is_staff)
def messbill(request):
    # Exports Mess Bill dues in an excel file
    # template: messbill.html

    if request.GET: # Not sure if this is required, but don't wanna break production (again)
        selected = request.GET['ids']
        values = [x for x in selected.split(',')]
    if request.POST:
        generated_form = MessBillForm(request.POST)

        if not generated_form.is_valid():
            return render(request, "messbill.html", {"form": generated_form})

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

        start_date = datetime.strptime(request.POST.get('dateStart'), '%d %B, %Y').date()
        end_date = datetime.strptime(request.POST.get('dateEnd'), '%d %B, %Y').date()
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
        messages.error(request, 'Exporting {} messoptions'.format(values.count()))
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

    form = MessBillForm()
    return render(request, "messbill.html", {"form": form})

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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
        'student': student,
        'tees': tees,
        'items': items,
        'option': option,
        'balance': balance,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
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
                if nick == None:
                    nick = ''
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
    
    with open(settings.CONSTANTS_LOCATION, 'r') as fp:
        data = json.load(fp)
    if student.advance_amount != None:
        main_amt = student.advance_amount
    elif student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

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
        'advance_amount': main_amt,
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
    elif request.user.is_staff:
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
        
        with open(settings.CONSTANTS_LOCATION, 'r') as fp:
            data = json.load(fp)
        if student.advance_amount != None:
            main_amt = student.advance_amount
        elif student.nophd():
            main_amt = data['phd-swd-advance']
        else:
            main_amt = data['swd-advance']
        balance = float(main_amt) - float(total_amount)

        context = {
           'hostels' : [i[0] for i in HOSTELS],
           'branches' : BRANCH,
           'permission': perm,
           'option' :option,
           'student' :student,
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
        if (all(not d for d in [name, bitsId, branch, hostel, room])):
            # Checks if at least one of the fields is non-empty.
            messages.error(request, "Please fill at least one field.")
            context['errors'] = ["Please fill at least one field."]
            if request.user.is_authenticated and \
                not is_warden(request.user) and \
                not is_hostelsuperintendent(request.user):
                return render(request, "search_logged_in.html", dict(context, **postContext))
            else:
                return render(request, "search.html", dict(context, **postContext))
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

        if students.count() == 0:
            messages.error(request, "No student found with these details.")
            context['errors'] = ["No student found with these details."]

    if request.user.is_authenticated and not is_warden(request.user) and not is_hostelsuperintendent(request.user):
        return render(request, "search_logged_in.html", dict(context, **postContext))
    else:
        return render(request, "search.html", dict(context, **postContext))



def notice(request):
    context = {
        'queryset' : Notice.objects.all().order_by('-id')
    }
    return render(request,"notice.html",context)

def antiragging(request):
    return render(request,"antiragging.html",{})

def swd(request):
    context = {
        'hostels' : len(HOSTELS)
    }
    return render(request,"swd.html",context)

def csa(request):
    y=1-(datetime.now().month-1)//6

    context = {
        'csa' : CSA.objects.all().order_by('priority'),
        'year' : datetime.now().year - y
    }
    return render(request,"csa.html",context)

def migration(request):
    return render(request,"migration.html",{})    

def sac(request):
    return render(request,"sac.html",{})
    
def contact(request):
     #imagesup = os.listdir("assets/img/superintendents")
     #print(imagesup)
     sid = HostelSuperintendent.objects.all()
     wa = Warden.objects.all()
     sup = []
     asup = []
     bw = []
     gw = []
     for s in sid:
         if s.chamber!= None and s.chamber[1:2] == "H":
             sup.append(s)
         elif s.chamber!= None and s.chamber[1:2]!="H":
             asup.append(s)
              
     for w in wa:
         if w.hostel!=None and w.hostel != "CH3" and w.hostel != "CH4" and w.hostel != "CH7" and w.hostel != "CH5" and w.hostel!="CH6":
             bw.append(w)
         else:
             gw.append(w)
     context = {
         'sup': sup,
         'asup': asup,
         'bw': bw,
         'gw': gw,
         #'isup':imagesup
     }
     return render(request, "contact.html", context)

def studentDetails(request,id=None):
    option = get_base_template(request)
    if request.user.is_authenticated:
        if is_warden(request.user) or is_hostelsuperintendent(request.user) or request.user.is_staff:
            student = Student.objects.get(id=id)
            res=HostelPS.objects.get(student__id=id)
            disco=Disco.objects.filter(student__id=id)
            context = {
                'student'  :student,
                'residence' :res,
                'disco' : disco,
                'option': option
            }
            return render(request,"studentdetails.html",context)
        else:
            messages.error(request, "Unauthorised access. Contact Admin.")
            return redirect('search')            
    else:
        messages.error(request, "Login to gain access.")
        return redirect('login')


@login_required
def notices(request):
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
            
            with open(settings.CONSTANTS_LOCATION, 'r') as fp:
                data = json.load(fp)
            if student.advance_amount != None:
                main_amt = student.advance_amount
            elif student.nophd():
                main_amt = data['phd-swd-advance']
            else:
                main_amt = data['swd-advance']
            balance = float(main_amt) - float(total_amount)
            
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
                'queryset' : Document.objects.all().order_by('-pk').filter(Q(hostels__contains=hostelps.hostel) | Q(hostels=None)),
                'option': option,
                'mess': mess,
                'balance': balance,
                'leaves': leaves,
                'bonafides': bonafides,
                'daypasss': daypasss,
            }
    return render(request,"notices.html",context)

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
                    # Format : Name | Bits ID | MESS | MONTH(1-12)
                    bid = str(i[1].value)
                    s = Student.objects.get(bitsId=bid)
                    # month = date.today().month + 1
                    month = int(i[3].value)
                    my = datetime(date.today().year, month, 1)
                    try:
                        messop = MessOption.objects.get(student=s, monthYear= my)
                        messop.mess = str(i[2].value)
                        messop.save()
                    except MessOption.DoesNotExist as e:
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
        grad_ps = HostelPS.objects.filter(Q(status__exact="Graduate") | Q(room="") | Q(room="0") | Q(room="0.0") | Q(student__bitsId__contains="PH") | Q(acadstudent=False) | Q(room=None))
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
                    # ID No | Name | Expense 1 | Expense 2 | ... | Expense N | advance_amount
                    #              [ DueCategory(expense 1), DueCategory(expense 2), ...]
                    if first_iter:
                        for i in range(2, len(row)-1): # advance_amount will be last column
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

                        # Check if the due already exists with same student
                        #   and same category, then overwrite that due object
                        #   instead of making new ones.

                        try:
                            # If there is a due with the same category name (i.e October Mess Bill '19, etc)
                            # we just overwrite it.
                            due = Due.objects.get(student=student,
                                                 due_category=category,
                                                 description=category.name)

                            if amount == 0 or due.amount == 0:
                                # Delete the old record if it exists
                                due.delete()
                            else:
                                # Update the old record if it exists
                                due.amount = amount
                                due.save()
                        except Due.DoesNotExist as e:
                            if amount == 0: continue

                            Due.objects.create(student=student,
                                               amount=amount,
                                               due_category=category,
                                               description=category.name,
                                               date_added=datetime.now().date())
                    
                    try:
                        student.advance_amount = row[len(row)-1].value
                        student.save()
                    except:
                        student.advance_amount = None
                        student.save()
                        continue
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
            
            with open(settings.CONSTANTS_LOCATION, 'r') as fp:
                data = json.load(fp)
            if student.advance_amount != None:
                main_amt = student.advance_amount
            elif student.nophd():
                main_amt = data['phd-swd-advance']
            else:
                main_amt = data['swd-advance']
            balance = float(main_amt) - float(total_amount)

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
                        continue
                    change = student.change_cgpa(float(row[header['CGPA']].value))
                    if change is False:
                        message_str = str(row[header['studentID']].value) + " does not have " \
                            "a valid CGPA " + str(row[header['CGPA']].value)
                        messages.add_message(request,
                                            message_tag, 
                                            message_str)
                    else:
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
            count_created = 0
            created = False
            idx = 1
            header = {}
            # Create a list of objects to be created (For bulk creation)
            creation_list = []
            # creation_threshold -> Arbitrary maximum number of objects to be stored in memory before creating in bulk
            creation_threshold = 150
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
                    password = User.objects.make_random_password()

                    # Date of Birth and Date of Admit
                    # These col values are expected to be in dd-Mon-yy format
                    # For Example: 07-Jan-97
                    
                    try:
                        user = User.objects.get(username=username)
                        user.email='random@hello.com',
                        user.password=password
                        user.save()
                    except User.DoesNotExist:
                        user = User.objects.create_user(
                            username=username,
                            email='random@hello.com',
                            password=password)

                    # Date of Birth and Date of Admit
                    # These col values are expected to be in dd-Mon-yy format
                    # For Example: 07-Jan-97
                    dob = row[header['Stu_DOB']]
                    
                    if dob.ctype == 1: # XL_CELL_TEXT
                        try:
                            rev_bDay = datetime.strptime(dob.value, '%d-%b-%Y').strftime('%Y-%m-%d')
                        except ValueError:
                            rev_bDay = datetime.strptime(dob.value, '%Y-%m-%d').strftime('%Y-%m-%d')
                        
                    elif (dob.ctype == 3): # XL_CELL_DATE
                        rev_bDay = xlrd.xldate.xldate_as_datetime(dob.value, 0)
                        
                    else:
                        rev_bDay = datetime.strptime('01Jan1985', '%d%b%Y')
                        
                    
                    do_admit = row[header['admit']]
                    
                    if (do_admit.ctype == 1): # XL_CELL_TEXT
                        try: 
                            rev_admit = datetime.strptime(do_admit.value, '%d/%m/%Y').strftime('%Y-%m-%d')
                        except ValueError:
                            rev_admit = datetime.strptime(do_admit.value, '%Y-%m-%d').strftime('%Y-%m-%d')
                        
                    elif do_admit.ctype == 3: # XL_CELL_DATE
                        rev_admit = xlrd.xldate.xldate_as_datetime(do_admit.value, 0)
                        
                    else:
                        rev_admit = datetime.strptime('01Jan1985', '%d%b%Y')

                    try:    
                        updated_vals = {
                            'bitsId':str(row[header['studentID']].value)[:15],
                            'name':str(row[header['name']].value)[:50],
                            'bDay':rev_bDay,
                            'admit':rev_admit,
                            'gender':str(row[header['Stu_gender']].value)[0],
                            'phone':str(row[header['stu_mobile']].value)[:15],
                            'email':str(row[header['stu_email (other then institute)']].value),
                            'address':str(row[header['ADDRESS']].value),
                            'bloodGroup':str(row[header['bloodgp']].value)[:10],
                            'parentName':str(row[header['fname']].value)[:50],
                            'parentPhone':str(row[header['parent mobno']].value)[:20],
                            'parentEmail':str(row[header['parent mail']].value)[:50]
                        }         
                        try:
                            obj = Student.objects.get(user=user)
                            for key, value in updated_vals.items():
                                #print(f"{key}, {value}")
                                if (value):
                                    setattr(obj, key, value)
                            obj.save()
                        except Student.DoesNotExist:
                            obj = Student(
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
                            parentEmail=str(row[header['parent mail']].value)[:50])
                            # Add to creation list
                            creation_list.append(obj)
                            
                            if len(creation_list) == creation_threshold:
                                # Create these student objects in bulk
                                Student.objects.bulk_create(creation_list)
                                # print(f">> CREATED IN BULK (at {count_created+1})")
                                creation_list.clear()

                            created = True
                        if created:
                            count_created = count_created + 1
                        else:
                            count = count + 1
                    except Exception:
                        message_str + studentID + " failed"

            # Create these student objects in bulk
            Student.objects.bulk_create(creation_list)

            message_str = str(count_created) + " new students added," + "\n" + str(count) + " students updated."
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
                        user.email = emailID
                        user.password = password
                        user.save()
                    except User.DoesNotExist:
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
            # Create a list of objects to be created (For bulk creation)
            creation_list = []
            # creation_threshold -> Arbitrary maximum number of objects to be stored in memory before creating in bulk
            creation_threshold = 150
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
                        student = Student.objects.filter(bitsId=row[header['studentID']].value).first()
                    except Student.DoesNotExist:
                        message_str = str(row[header['studentID']].value) + " does not exist in database \n"
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
                        acadstudent = True
                        status = ''
                        new_hostel = row[header['Hostel']].value
                        if new_hostel == 'Graduate' or new_hostel == 'Faculty' or new_hostel == 'Part Time' or new_hostel == 'Permanent Withdrawal' or new_hostel == 'Temporary Withdrawal' or new_hostel == 'Registration Cancelled' or new_hostel == 'Withdrawal':
                            acadstudent=False
                            status = new_hostel
                        else:
                            acadstudent=True
                            status = "Student"
                        if row[header['Room']].value:
                            try:
                                room = str(int(row[header['Room']].value))
                            except Exception:
                                room = str(row[header['Room']].value)
                        else:
                            room = ''

                        # If a student is there in the sheet but not in the database, ignore
                        if(student == None):
                            continue

                        hostelps = HostelPS(student=student, hostel=new_hostel, room=room, acadstudent=acadstudent, status=status, psStation="")
                        creation_list.append(hostelps)
                            
                        if len(creation_list) == creation_threshold:
                            # Create these hostelps objects in bulk
                            HostelPS.objects.bulk_create(creation_list)
                            # print(f">> CREATED IN BULK (at {count_created+1})")
                            creation_list.clear()

                        count = count + 1
                    if message_str is not '':
                        messages.add_message(request,
                            message_tag, 
                            message_str)

            # Create these student objects in bulk
            HostelPS.objects.bulk_create(creation_list)

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
                            d = datetime(*xlrd.xldate_as_tuple(excel_date, 0)).date()
                            excel_time = row[header['time']].value
                            t = datetime(*xlrd.xldate_as_tuple(excel_date + excel_time, 0)).time()
                            d_t = datetime.combine(d, t)
                            LateComer.objects.create(
                                student = s,
                                dateTime = d_t
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
                    #try:
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
                    #except Exception as e:
                        #message_str = str(e)
                        #messages.add_message(request,
                        #message_tag, 
                        #message_str)
                    
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
def update_names(request):
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
                    return render(request, "add_students.html", {'header': "Update Names"})

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
                    
                    Student.objects.filter(
                        bitsId=row[header['studentID']].value
                        ).update(name=str(row[header['Name']].value))
                    
                    count = count + 1
            message_str = str(count) + " Updated students' names"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Names"})

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
                        hostel = HostelPS.objects.filter(student=student[0]).update(hostel='', room='', acadstudent=False, status=row[header['Status']].value, psStation=row[header['PS Station']].value)
                        count = count + 1
                    except Exception:
                        message_str + "update failed for " + row[header['studentID']].value
                    
            message_str = str(count) + " Updated PS/Thesis"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update PS/Thesis"})


@user_passes_test(lambda u: u.is_staff)
def export_mess_leave(request):
    if not request.POST:
        return render(request, "export_mess_leave.html")

    # Handle the POST request (i.e. generate Excel sheet)
    
    year = int(request.POST["year"])
    month = int(request.POST["month"])
    mess = request.POST["mess"]

    # WHAT TO DO:
    # First get students in that mess from messOption
    # Get leaves of all these students' leaves with start or end date containing month
    
    # Get students in that mess
    students = MessOption.objects.filter(mess=mess).values_list("student", flat=True)

    # This is a query for getting leaves of these students if they intersect the selected duration
    query = Q(student__in=students) & ( 
        Q(dateTimeStart__month__exact=month, dateTimeStart__year__exact=year) |\
        Q(dateTimeEnd__month__exact=month, dateTimeEnd__year__exact=year)
    )

    # Use the above query, and also make sure leaves are approved
    leaves = Leave.objects.filter(query, approved__exact=True)
    
    # At this point, leaves is a QuerySet containing approved leaves in that month and year from that mess

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{mess} Mess Leaves {month_name[month]}, {year}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Mess Leave Details')

    heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
    h2_style = xlwt.easyxf('font: bold on; align: vert centre, horiz centre')
    font_style = xlwt.easyxf('font: bold on')

    columns = [
        ('ID', 4000),
        ('Name', 4000),
        ('Leave Start', 8000),
        ('Leave End', 8000),
        ('Leave Duration', 4000)
    ]

    # Write the heading
    ws.write_merge(0, 0, 0, len(columns)-1, f"{mess} Mess Leaves - {month_name[month]}, {year}", heading_style)

    # Write the column titles
    for i, (col_name, col_width) in enumerate(columns):
        ws.write(1, i, col_name, h2_style)
        ws.col(i).width = col_width

    _, DAYS_IN_MONTH = monthrange(year, month)

    font_style = xlwt.XFStyle()
    for row_num, leave in enumerate(leaves, start=2):
        # First day of the leave within the given month
        start_day = leave.dateTimeStart.day # 1 indexed
        if(leave.dateTimeStart.month < month):
            start_day = 1
        
        # Last day of the leave within the given month
        end_day = leave.dateTimeEnd.day # 1 indexed
        if(leave.dateTimeEnd.month > month):
            end_day = DAYS_IN_MONTH
        
        # Number of leave days within the given period
        leave_duration = (end_day - start_day) + 1

        row_contents = [leave.student.bitsId, leave.student.name, leave.dateTimeStart, leave.dateTimeEnd, leave_duration]

        for col_num, content in enumerate(row_contents):
            ws.write(row_num, col_num, str(content), font_style)

    wb.save(response)
    return response

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
                        student.bank_account_no = str(row[header['account']].value)
                        student.save()
                        count+=1
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

@user_passes_test(lambda u: u.is_superuser)
def update_parent_email(request):
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
                    return render(request, "add_students.html", {'header': "Update Parent Email"})
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
                        student.parentEmail = str(row[header['parentEmail']].value)
                        student.save()
                        count+=1
                    except Exception:
                        message_str + "student " + row[header['studentID']].value + " not in database"
                    
            message_str = str(count) + " Updated Parent Email"
        else:
            message_str = "No File Uploaded."
    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Update Parent Email"})

@user_passes_test(lambda u: u.is_staff)
def leave_export(request):
    if request.POST:
        d = datetime.strptime(request.POST.get('date'), '%d %B, %Y').date()
        approved = Leave.objects.filter(approved__exact=True, dateTimeStart__date__exact=d)
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+ "Leaves.xls"
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("leaves")

        heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
        h2_font_style = xlwt.easyxf('font: bold on')
        font_style = xlwt.easyxf('align: wrap on')

        
        columns = [
            (u"studentID", 6000),
            (u"Name", 6000),
            (u"reason", 6000),
            (u"Start Date", 6000),
            (u"End Date", 6000),
           ]

        row_num = 0


        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], h2_font_style)
            ws.col(col_num).width = columns[col_num][1]

        for i in approved:
            obj = i.student
            row = [
                obj.bitsId,
                obj.name,
                i.reason,
                str(i.dateTimeStart.astimezone(timezone("Asia/Kolkata")).date()),
                str(i.dateTimeEnd.astimezone(timezone("Asia/Kolkata")).date()),
            ]
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        messages.success(request, "Export done. Download will automatically start.")
        return response
    return render(request, "leave_export.html", {})

@user_passes_test(lambda u: u.is_superuser)
def hostel_export(request):
    if request.POST:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+ 'hostel export.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("hostel")

        heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
        h2_font_style = xlwt.easyxf('font: bold on')
        font_style = xlwt.easyxf('align: wrap on')

        # This function is not documented but given in examples of repo
        #     here: https://github.com/python-excel/xlwt/blob/master/examples/merged.py
        # Prototype:
        #     sheet.write_merge(row1, row2, col1, col2, 'text', fontStyle)
        
        query = HostelPS.objects.all().exclude(room=None)
        columns = [
                (u"studentID", 6000),
                (u"Hostel", 6000),
                (u"Room", 6000),
               ]

        row_num = 0


        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], h2_font_style)
            ws.col(col_num).width = columns[col_num][1]

        for i in query:
            obj = i.student
            row = [
                obj.bitsId,
                i.hostel,
                i.room
            ]
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        messages.success(request, "Export done. Download will automatically start.")
        return response
    return render(request, "mess_export.html", {})

@user_passes_test(lambda u: u.is_superuser)
def leave_import(request):
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
                    return render(request, "add_students.html", {'header': "Leave import"})

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
                        student = Student.objects.get(user__username=row[header['loginID']].value)
                        sdate = row[header['sdate']].value
                        stime = row[header['stime']].value
                        edate = row[header['edate']].value
                        etime = row[header['etime']].value
                        reason = row[header['reason']].value
                        approved_by = row[header['approved_by']].value
                        warden_approv = row[header['warden_approv']].value
                        addr = row[header['addr']].value
                        ph = row[header['ph']].value
                        comment = row[header['comment']].value
                    except Exception:
                        message_str + "student " + row[header['loginID']].value + " not in database"
                    rev_sdate = datetime(*xlrd.xldate_as_tuple(sdate, 0)).date()
                    #stime = datetime.combine(rev_sdate, stime)
                    rev_stime = datetime(*xlrd.xldate_as_tuple(sdate+stime, 0)).time()
                    sdatetime = datetime.combine(rev_sdate, rev_stime)
                    rev_edate=  datetime(*xlrd.xldate_as_tuple(edate, 0)).date()
                    #etime = datetime.combine(rev_edate, etime)
                    rev_etime = datetime(*xlrd.xldate_as_tuple(edate+etime, 0)).time()
                    edatetime = datetime.combine(rev_edate, rev_etime)
                    try:
                        warden = Warden.objects.get(user__username=approved_by)
                    except:
                        warden = None
                    if warden_approv == 'disapprov':
                        approved=False
                        inprocess=False
                        disapproved=True
                    elif warden_approv == 'YES':
                        approved=True
                        inprocess=False
                        disapproved=False
                    else:
                        approved=False
                        inprocess=True
                        disapproved=False
                    Leave.objects.create(student=student, dateTimeStart=make_aware(sdatetime), dateTimeEnd=make_aware(edatetime), reason=reason, consent=consent, corrAddress=addr, corrPhone=ph, approvedBy=warden, approved=approved, disapproved=disapproved, inprocess=inprocess, comment=comment)
                    
                    
            message_str = str(count) + " Leave imported"
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "add_students.html", {'header': "Leave Import"})

@user_passes_test(lambda u: u.is_superuser)
def leave_diff(request):
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

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename='+ 'hostel export.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet("hostel")

            heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
            h2_font_style = xlwt.easyxf('font: bold on')
            font_style = xlwt.easyxf('align: wrap on')
            
            columns = [
                    (u"loginID", 6000),
                    (u"sdate", 6000),
                    (u"stime", 6000),
                    (u"edate", 6000),
                    (u"etime", 6000),
                    (u"reason", 6000),
                    (u"approved_by", 6000),
                    (u"warden_approv", 6000),
                    (u"addr", 6000),
                    (u"ph", 6000),
                    (u"comment", 6000),
                    (u"consent", 6000),
                   ]

            row_num = 0

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num][0], h2_font_style)
                ws.col(col_num).width = columns[col_num][1]


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

                    loginID = row[header['loginID']].value
                    student = Student.objects.get(user__username = loginID)

                    try:
                        sdate = row[header['sdate']].value
                        stime = row[header['stime']].value
                        edate = row[header['edate']].value
                        etime = row[header['etime']].value
                        rev_sdate = datetime(*xlrd.xldate_as_tuple(sdate, 0)).date()
                        rev_stime = datetime(*xlrd.xldate_as_tuple(sdate+stime, 0)).time()
                        sdatetime = datetime.combine(rev_sdate, rev_stime)
                        rev_edate=  datetime(*xlrd.xldate_as_tuple(edate, 0)).date()
                        rev_etime = datetime(*xlrd.xldate_as_tuple(edate+etime, 0)).time()
                        edatetime = datetime.combine(rev_edate, rev_etime)
                        warden_approv = row[header['warden_approv']].value
                        if warden_approv == 'disapprov':
                            approved=False
                            inprocess=False
                            disapproved=True
                        elif warden_approv == 'YES':
                            approved=True
                            inprocess=False
                            disapproved=False
                        else:
                            approved=False
                            inprocess=True
                            disapproved=False
                        Leave.objects.get(student = student, dateTimeStart__date = rev_sdate, approved=approved, disapproved=False, inprocess=False)
                    except Leave.DoesNotExist:
                        row = [
                            row[header['loginID']].value,
                            row[header['sdate']].value,
                            row[header['stime']].value,
                            row[header['edate']].value,
                            row[header['etime']].value,
                            row[header['reason']].value,
                            row[header['approved_by']].value,
                            row[header['warden_approv']].value,
                            row[header['addr']].value,
                            row[header['ph']].value,
                            row[header['comment']].value,
                            row[header['consent']].value,
                        ]
                        row_num += 1
                        for col_num in range(len(row)):
                            ws.write(row_num, col_num, row[col_num], font_style)


            wb.save(response)
            messages.success(request, "Export done. Download will automatically start.")
            return response
    return render(request, "add_students.html", {'header': "Leave Missing Export"})    

@user_passes_test(lambda u: u.is_superuser)
def get_corr_address(request):
    if request.POST:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+ 'hostel export.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("hostel")

        heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
        h2_font_style = xlwt.easyxf('font: bold on')
        font_style = xlwt.easyxf('align: wrap on')

        # This function is not documented but given in examples of repo
        #     here: https://github.com/python-excel/xlwt/blob/master/examples/merged.py
        # Prototype:
        #     sheet.write_merge(row1, row2, col1, col2, 'text', fontStyle)
        ds = datetime(year=2020, month=3, day=1)
        #ds = ds.strftime('%Y-%m-%d')
        de = datetime(year=2020, month=3, day=15)
        #de = de.strftime('%Y-%m-%d')
        query = Leave.objects.filter(dateTimeStart__date__gte = ds, dateTimeEnd__date__lte = de ,approved = True)
        columns = [
                (u"studentID", 6000),
                (u"Name", 6000),
                (u"Corr address", 6000),
                (u"start date", 6000),
                (u"end date", 6000),
                
               ]

        row_num = 0


        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], h2_font_style)
            ws.col(col_num).width = columns[col_num][1]

        for i in query:
            obj = i.student
            row = [
                obj.bitsId,
                obj.name,
                i.corrAddress,
                i.dateTimeStart.replace(tzinfo=None).strftime('%d-%m-%Y'),
                i.dateTimeEnd.replace(tzinfo=None).strftime('%d-%m-%Y'),
            ]
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
        wb.save(response)
        messages.success(request, "Export done. Download will automatically start.")
        return response
    return render(request, "add_students.html", {})


@user_passes_test(lambda u: u.is_superuser)
def upload_profile_pictures(request):
    if request.POST:
        if request.FILES:
            error_files = []
            successfull = 0
            for filex in request.FILES.getlist('folder'):
                file_name, file_ext = filex.name.split('.')
                file_name = file_name.upper()
                try:
                    student = Student.objects.get(bitsId=file_name)
                    student.profile_picture.save(
                        file_name, filex
                    )
                    successfull += 1
                except Student.DoesNotExist:
                    error_files.append(file_name.lower())
            
            if len(error_files):
                messages.error(
                    request,
                    str(len(error_files)) + " IDs did not match: " + \
                        ", ".join(error_files))
            if (successfull):
                messages.success(request, str(successfull) + " IDs updated.")
        else:
            messages.error(
                request, "No folder selected. Please select at least one.")
       
    return render(request, "upload_profile_pictures.html", {})

@user_passes_test(lambda u: u.is_superuser)
def upload_contact_pictures(request):
    if request.POST:
        if request.FILES:
            error_files = []
            successfull = 0
            for filex in request.FILES.getlist('folder'):
                file_name = filex.name
                try:
                    path = no_duplicate_storage.save(file_name, filex)
                    successfull+=1
                except Exception:
                    error_files.append(file_name.lower())
            
            if len(error_files):
                messages.error(
                    request,
                    str(len(error_files)) + " IDs did not match: " + \
                        ", ".join(error_files))
            if (successfull):
                messages.success(request, str(successfull) + " files uploaded.")
        else:
            messages.error(
                request, "No folder selected. Please select at least one.")
       
    return render(request, "upload_contact_pictures.html", {})

@user_passes_test(lambda u: u.is_superuser)
def delete_students(request):
    """
        Takes Excel Sheet as FILE input.
        Deletes Students from the database.
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
                    return render(request, "del_students.html", {})

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
                    
                    # create User model
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
                    
                    try:
                        user = User.objects.get(username=username)
                        user.delete()
                        count = count + 1
                        # student = Student.objects.get(bitsId=studentID)
                        # student.delete()
                    
                    except User.DoesNotExist:
                        message_str += studentID + " failed\n"
                            
            message_str += str(count) + " students deleted."
        else:
            message_str = "No File Uploaded."

    if message_str is not '':
        messages.add_message(request,
                            message_tag, 
                            message_str)
    return render(request, "del_students.html", {'header': "Delete existing students from Database"})

def messagefromdean(request):
    return render(request,"messagefromdean.html",{})
