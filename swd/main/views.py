from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, MessOptionOpen, MessOption, Leave, Bonafide, Warden, DayPass, MessBill, HostelPS, TeeAdd, TeeBuy, ItemAdd, ItemBuy
from django.views.decorators.csrf import csrf_protect
from datetime import date, datetime, timedelta
from .forms import MessForm, LeaveForm, BonafideForm, DayPassForm
from django.contrib import messages
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.conf import settings

from braces import views

from django.contrib.auth.models import User

from calendar import monthrange

from django.contrib import messages

def noPhD(func):
    def check(request, *args, **kwargs):
        student = Student.objects.get(user=request.user)
        if student.nophd():
            return redirect("/dashboard/")
        return func(request, *args, **kwargs)
    return check

def index(request):
    return render(request, 'home1.html',{})


def login_success(request):
    return HttpResponse("Success!")

@login_required
def studentimg(request):
    url = Student.objects.get(user=request.user).profile_picture
    print(url)
    ext = url.name.split('.')[-1]
    
    try:
        with open(url.name, "rb") as f:
            return HttpResponse(f.read(), content_type="image/"+ext)
    except IOError:
        with open("assets/img/profile-swd.jpg", "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpg")

@login_required
def documents(request):
    student = Student.objects.get(user=request.user)
    return render(request, "documents.html", {'student': student})

@login_required
def dashboard(request):
    student = Student.objects.get(user=request.user)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=date.today() - timedelta(days=7))
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=date.today() - timedelta(days=7))
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=date.today() - timedelta(days=7))
    address = student.address
    context = {
        'student': student,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        'address': address
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
            'address': address
            }
    elif messopen and messoption:
        context = {
            'option': 1,
            'mess': messoption[0].mess,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            'address': address
            }
    else:
        context = {
            'option': 2,
            'student': student,
            'leaves': leaves,
            'bonafides': bonafides,
            'daypasss': daypasss,
            'address': address
            }

    if request.POST:
        address = request.POST.get('address')
        #print(address)
        student.address = address
        student.save()
        return HttpResponse("{ status: 'ok' }")

    return render(request, "dashboard.html", context)


@login_required
def profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    print(student.name)
    return render(request, "profile.html", context)


@csrf_protect
def loginform(request):

    if request.user.is_authenticated:
        if request.user.is_staff:
                return redirect('/admin')
        if Warden.objects.filter(user=request.user):
            return redirect('/warden')
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
@noPhD
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
            leaveform.corrPhone = request.POST.get('phone_number')
            leaveform.dateTimeStart = make_aware(dateTimeStart)
            leaveform.dateTimeEnd = make_aware(dateTimeEnd)
            leaveform.student = student
            print(request.POST.get('consent'))
            leaveform.save()
            #email_to=[Warden.objects.get(hostel=HostelPS.objects.get(student=student).hostel).email]             # For production
            #email_to=["youremail@site.com"]                                                                      # For testing 
            mailObj=Leave.objects.latest('id')
            mail_subject="New Leave ID: "+ str(mailObj.id)
            mail_message="Leave Application applied by "+ mailObj.student.name +" with leave id: " + str(mailObj.id) + ".\n"
            mail_message=mail_message + "Parent name: " + mailObj.student.parentName + "\nParent Email: "+ mailObj.student.parentEmail + "\nParent Phone: " + mailObj.student.parentPhone
            mail_message=mail_message + "\nConsent type: " + mailObj.consent
            send_mail(mail_subject,mail_message,settings.EMAIL_HOST_USER,email_to,fail_silently=False)

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
                'form': form
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
                    'option': 1,
                }
            else:
                context = {
                    'option': 2,
                }
    else:
        context = {
              'option': 3,
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

@login_required
@user_passes_test(is_warden)
def warden(request):
    warden = Warden.objects.get(user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel__icontains=warden.hostel).order_by('approved', '-id')
    daypasss = DayPass.objects.filter(student__hostelps__hostel__icontains=warden.hostel).order_by('approved', '-id')
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
        mail_message={}
        #email_to = [leave.student.email]                         # For production
        #email_to = ["youremail@site.com"]                        # For testing
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
@user_passes_test(is_warden)
def wardendaypassapprove(request, daypass):
    daypass = DayPass.objects.get(id=daypass)
    warden = Warden.objects.get(user=request.user)
    leaves = Leave.objects.filter(student__hostelps__hostel__icontains=warden.hostel).order_by('approved', '-id')
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
                'form': form
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
        ws = wb.add_sheet("A Mess")
        ws2 = wb.add_sheet("C Mess")
        ws3 = wb.add_sheet("Indeterminate")

        row_num = 0
        row_num_2 = 0
        row_num_3 = 0

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
            ws2.write(row_num, col_num, columns[col_num][0], font_style)
            ws3.write(row_num, col_num, columns[col_num][0], font_style)
            # set column width
            ws.col(col_num).width = columns[col_num][1]
            ws2.col(col_num).width = columns[col_num][1]
            ws3.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        start_date = datetime.strptime(request.POST.get('start_date'), '%d %B, %Y').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%d %B, %Y').date()

        messbill = MessBill.objects.first()
        amount = messbill.amount
        rebate = messbill.rebate

        end_date = end_date if end_date<date.today() else date.today()

        days = end_date - start_date
        days = days.days + 1

        if request.POST.get('mess') is not 'N':
            values = MessOption.objects.filter(mess=request.POST.get(
                'mess'), monthYear=start_date.replace(day=1))
        for k in values:
            if request.POST.get('mess') is not 'N':
                obj = k.student
            else:
                obj = Student.objects.get(bitsId=k)
                try:
                    mess = MessOption.objects.get(
                        student=obj, monthYear=start_date.replace(day=1))
                except:
                    mess = MessOption.objects.create(
                        student=obj, monthYear=start_date.replace(day=1), mess='N')

            leaves = Leave.objects.filter(student=obj)

            noofdays = 0

            for leave in leaves:
                if leave.approved == True:
                    if leave.dateTimeStart.date() >= start_date and leave.dateTimeStart.date() <= end_date and leave.dateTimeEnd.date() >= end_date:
                        noofdays += abs(end_date -
                                        leave.dateTimeStart.date()).days + 1
                    elif leave.dateTimeEnd.date() >= start_date and leave.dateTimeEnd.date() <= end_date and leave.dateTimeStart.date() <= start_date:
                        noofdays += abs(leave.dateTimeEnd.date() -
                                        start_date).days + 1
                    elif leave.dateTimeStart.date() >= start_date and leave.dateTimeEnd.date() <= end_date:
                        noofdays += abs(leave.dateTimeEnd.date() -
                                        leave.dateTimeStart.date()).days + 1
                    elif leave.dateTimeStart.date() <= start_date and leave.dateTimeEnd.date() >= end_date:
                        noofdays += abs(end_date - start_date).days + 1
            finalamt = amount * days - rebate * noofdays

            row = [
                obj.name,
                obj.bitsId,
                amount * days,
                rebate * noofdays,
                finalamt
            ]

            if request.POST.get('mess') is not 'N':
                row_num += 1
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)
            else:
                if mess.mess == 'A':
                    row_num += 1
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, row[col_num], font_style)
                elif mess.mess == 'C':
                    row_num_2 += 1
                    for col_num in range(len(row)):
                        ws2.write(row_num_2, col_num, row[col_num], font_style)
                else:
                    row_num_3 += 1
                    for col_num in range(len(row)):
                        ws3.write(row_num_3, col_num, row[col_num], font_style)

        wb.save(response)
        return response

    return render(request, "messbill.html", {})

def store(request):
    student = Student.objects.get(user=request.user)
    tees = TeeAdd.objects.filter(available=True)
    items = ItemAdd.objects.filter(available=True)
    teesj = TeeAdd.objects.filter(available=True).values_list('title')
    # tees_json = json.dumps(list(tees), cls=DjangoJSONEncoder)
    context = {
        'student': student,
        'tees': tees,
        'items': items,
        # 'tees_json': tees_json,
    }

    if request.POST:
        if request.POST.get('what') == 'item':
            itemno = ItemAdd.objects.get(id=int(request.POST.get('info')))
            if itemno.available == True:
                itembuy = ItemBuy.objects.create(item = itemno, student=student)
                messages.add_message(request, messages.INFO, itemno.title + ' item bought. Thank you for purchasing. Headover to DUES to check your purchases.', extra_tags='green')
            messages.add_message(request, messages.INFO,  'Item not available', extra_tags='red')
        if request.POST.get('what') == 'tee':
            teeno = TeeAdd.objects.get(id=int(request.POST.get('info')))
            try:
                nick = request.POST.get('nick')
                sizes = request.POST.get('sizes')
                colors = request.POST.get('colors')
                qty = request.POST.get('quantity')
                # Validation
                message_error = ""
                if teeno.nick == True:
                    if nick == "":
                        message_error = "No nick provided. Please provide a nick."
                if teeno.sizes and sizes not in teeno.sizes.split(','):
                    message_error = "Size doesn't match the database."
                if teeno.colors and colors not in teeno.colors.split(','):
                    message_error = "Color doesn't match the database."
                if qty is None:
                    message_error = "Provide quantity of the tees you want."
                print(message_error)
                if message_error == "":
                    teebuy = TeeBuy.objects.create(tee = teeno, student=student, nick=nick, size=sizes, color=colors, qty=qty)
                    messages.add_message(request, messages.INFO, teeno.title + ' tee bought. Thank you for purchasing. Headover to DUES to check your purchases.', extra_tags='green')
                else:
                    messages.add_message(request, messages.INFO,  message_error, extra_tags='red')

            except Exception as e:
                print(e)
                print("Failed")
            # teebuy = TeeBuy.objects.create(tee = teeno, student=student, )
    return render(request, "store.html", context)


def dues(request):
    student = Student.objects.get(user=request.user)
    month = datetime.today().month
    itemdues = ItemBuy.objects.filter(student=student, created__month=month)
    teedues = TeeBuy.objects.filter(student=student, created__month=month)
    context = {
        'student' : student,
        'itemdues' : itemdues,
        'teedues' : teedues,
    }

    return render(request, "dues.html", context)