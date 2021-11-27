import json
import xlwt
from datetime import datetime, date, timedelta

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import make_aware
from django.http import HttpResponse

from swd import settings
from .models import MCNApplication, MCNApplicationPeriod
from main.models import Student, Leave, DayPass, Bonafide, Due, TeeBuy, ItemBuy, MessOptionOpen, MessOption


@login_required
def submit_mcn(request):

    # =================== LEFT PANEL ===================

    student = Student.objects.get(user=request.user)

    timediff = date.today() - timedelta(days=7)
    leaves = Leave.objects.filter(student=student, dateTimeStart__gte=timediff)
    daypasss = DayPass.objects.filter(student=student, dateTime__gte=timediff)
    bonafides = Bonafide.objects.filter(student=student, reqDate__gte=timediff)

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
    if student.nophd():
        main_amt = data['phd-swd-advance']
    else:
        main_amt = data['swd-advance']
    balance = float(main_amt) - float(total_amount)

    context = {
        'student': student,
        'balance': balance,
        'option': option,
        'mess': mess,
        'leaves': leaves,
        'bonafides': bonafides,
        'daypasss': daypasss,
        'errors': []
    }

    # =================== SUBMISSION ===================

    currentDate = datetime.now()
    yr1 = currentDate.year
    yr2 = yr1
    if currentDate.month < 8:
        # Even Semester
        yr2 -= 1
        yr1 -= 2
    else:
        # Odd Semester
        yr1 -= 1
    context['itr_year'] = str(yr1+1) + "-" + str((yr2+1) % 100)

    mcn_period = MCNApplicationPeriod.objects.filter(Open__lte=currentDate, Close__gte=currentDate).last()
    if mcn_period and mcn_period.Batch != "":
        if(request.user.student.bitsId[:4] not in mcn_period.Batch):
            mcn_period = None
    context['mcn_period'] = mcn_period

    already_submitted = MCNApplication.objects.filter(student=request.user.student, ApplicationPeriod=mcn_period).last()
    context['already_submitted'] = already_submitted

    if request.method == 'POST' and mcn_period and already_submitted is None:
        FathersIncome = request.POST['FathersIncome']
        FathersIncome = 0 if FathersIncome is '' else int(FathersIncome)

        MothersIncome = request.POST['MothersIncome']
        MothersIncome = 0 if MothersIncome is '' else int(MothersIncome)
        MothersName = request.POST['MothersName']
        FathersIncomeDoc = request.FILES.get('FathersIncomeDoc', None)
        MothersIncomeDoc = request.FILES.get('MothersIncomeDoc', None)
        
        TehsildarCertificate = request.FILES.get('TehsildarCertificate', None)
        BankPassbook = request.FILES.get('BankPassbook', None)

        tehsil = ((TehsildarCertificate) or (BankPassbook))

        if MothersName == '' and MothersIncomeDoc is not None:
            context['errors'].append("Please enter mother's name")
            return render(request, "mcn_submit.html", context)

        if FathersIncome == 0 and MothersIncome == 0:
            context['errors'].append("Please enter income of earning parent.")
            return render(request, "mcn_submit.html", context)
        else:
            if (FathersIncome != 0) and (not FathersIncomeDoc) and (not tehsil):
                context['errors'].append("Please upload proof of Father\'s Income.")
                return render(request, "mcn_submit.html", context)
            if (MothersIncome != 0) and (not MothersIncomeDoc) and (not tehsil):
                context['errors'].append("Please upload proof of Mother\'s Income.")
                return render(request, "mcn_submit.html", context)

        if (FathersIncomeDoc is None) and (MothersIncomeDoc is None):
            # If neither of father's or mother's income certificate is uploaded
            # check if both Tehsil Certificate and Passbook are uploaded
            if TehsildarCertificate is None or BankPassbook is None:
                doc_error_str = "Please upload both Tehsildar's Certificate and Bank Passbook" \
                                                    " or earning parent's income certificate"
                context['errors'].append(doc_error_str)
                return render(request, "mcn_submit.html", context)

        supported_exts = ['pdf']

        for doc in [MothersIncomeDoc, FathersIncomeDoc, TehsildarCertificate, BankPassbook]:
            if doc is not None:
                ext = doc.name.split('.')[-1]
                if ext not in supported_exts:
                    msg_txt = "Invalid uploaded document type of {}".format(doc.name)
                    msg_txt += ", it should be one of "
                    msg_txt += ', '.join(supported_exts)
                    context['errors'].append(msg_txt)

                if doc.size > settings.MAX_MCN_UPLOAD_SIZE:
                    msg_txt = "Uploaded document {}".format(doc.name)
                    msg_txt += " should be of less than "
                    msg_txt += str(settings.MAX_MCN_UPLOAD_SIZE) + " bytes."
                    context['errors'].append(msg_txt)

        if len(context['errors']):
            return render(request, "mcn_submit.html", context)

        mcn_application = MCNApplication.objects.create(
            student=student,
            ApplicationPeriod=mcn_period,
            FathersIncome=FathersIncome,
            FathersIncomeDoc=FathersIncomeDoc,
            MothersIncome=MothersIncome,
            MothersIncomeDoc=MothersIncomeDoc,
            TehsildarCertificate=TehsildarCertificate,
            BankPassbook=BankPassbook,
            MothersName=MothersName
            )

        context['success'] = True

    return render(request, "mcn_submit.html", context)


@user_passes_test(lambda u: u.is_staff)
def export_mcn_approved(request, mcn_period_pk, filter_criteria):
    mcn_period = get_object_or_404(MCNApplicationPeriod, pk=mcn_period_pk)

    if filter_criteria == 'approved':
        mcn_applications = MCNApplication.objects.filter(
            ApplicationPeriod=mcn_period, approved=True, rejected=False)
    elif filter_criteria == 'rejected':
        mcn_applications = MCNApplication.objects.filter(
            ApplicationPeriod=mcn_period, approved=False, rejected=True)
    elif filter_criteria == 'all':
        mcn_applications = MCNApplication.objects.filter(
            ApplicationPeriod=mcn_period)
    else:
        return HttpResponse(request, 'Invalid Request')
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="mcn_export.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MCN Applications')

    heading_style = xlwt.easyxf('font: bold on, height 280; align: wrap on, vert centre, horiz center')
    h2_font_style = xlwt.easyxf('font: bold on')
    font_style = xlwt.easyxf('align: wrap on')
    
    ws.write_merge(0, 0, 0, 6, "{} MCN Applications: {}".format(
        filter_criteria, mcn_period.Name), heading_style)
    ws.write(1, 0, "Student ID", h2_font_style)
    ws.write(1, 1, "Student Name", h2_font_style)
    ws.write(1, 2, "Fathers Name", h2_font_style)
    ws.write(1, 3, "Fathers Income", h2_font_style)
    ws.write(1, 4, "Mothers Name", h2_font_style)
    ws.write(1, 5, "Mothers Income", h2_font_style)
    ws.write(1, 6, "Gross Income", h2_font_style)
    ws.write(1, 7, "Status", h2_font_style)
    ws.write(1, 8, "Fathers Income Doc", h2_font_style)
    ws.write(1, 9, "Mothers Income Doc", h2_font_style)
    ws.write(1, 10, "Tehsildar Certificate", h2_font_style)
    ws.write(1, 11, "Bank Passbook", h2_font_style)

    for idx, application in enumerate(mcn_applications):
        student = application.student
        ws.write(2 + idx, 0, student.bitsId, font_style)
        ws.write(2 + idx, 1, student.name, font_style)
        ws.write(2 + idx, 2, student.parentName, font_style)
        x = application.FathersIncome
        ws.write(2 + idx, 3, x, font_style)
        
        # TODO: Add mothers name in database
        ws.write(2 + idx, 4, 'MotherName', font_style)
        y = application.MothersIncome
        ws.write(2 + idx, 5, y, font_style)
        ws.write(2 + idx, 6, x + y, font_style)
        if application.approved:
            status = 'Approved'
        elif application.rejected:
            status = 'Rejected'
        else:
            status = ''
        ws.write(2 + idx, 7, status, font_style)
        for docdx, doc in enumerate([application.FathersIncomeDoc, application.MothersIncomeDoc,
                            application.TehsildarCertificate, application.BankPassbook]):
            try:
                url = xlwt.Formula('HYPERLINK("%s";"Link")' % request.build_absolute_uri(doc.url))
            except ValueError:
                # Raised when doc not uploaded
                url = 'None'
            ws.write(2 + idx, 8 + docdx, url, font_style)
    
    wb.save(response)
    return response
