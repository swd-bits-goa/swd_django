from django.shortcuts import render
from .models import MCNApplication, MCNApplicationPeriod
from datetime import datetime


def submit_mcn(request):
    """
    View handles when student views/edits/submits MCN application.
    """
    if request.method == 'POST':
        DateTimeSubmitted = request.POST['DateTimeSubmitted']
        FathersIncome = request.POST['FathersIncome']
        MothersIncome = request.POST['MothersIncome']
        FathersIncomeDoc = request.FILES.get['FathersIncomeDoc', None]
        MothersIncomeDoc = request.FILES.get['MothersIncomeDoc', None]
        TehsildarCertificate = request.FILES.get['TehsildarCertificate', None]
        BankPassbook = request.FILES.get['BankPassbook', None]

    openDate = datetime.strptime('%d %B, %Y').date()
    closeDate = datetime.strptime('%d %B %Y').date()
    currentDate = datetime.now().date()

    mcn_period = MCNApplication.objects.filter(Open=openDate, Close=closeDate)

    if (currentDate > openDate):
        if(currentDate < closeDate):
            mcn_application = MCNApplication(student=request.user, MCNApplicationPeriod=mcn_period, DateTimeSubmitted=DateTimeSubmitted, FathersIncome=FathersIncome, MothersIncome=MothersIncome,
                                             FathersIncomeDoc=FathersIncomeDoc, MothersIncomeDoc=MothersIncomeDoc, TehsildarCertificate=TehsildarCertificate, BankPassbook=BankPassbook)
            mcn_application.save()

    return render(request, 'mcn_submit.html')
