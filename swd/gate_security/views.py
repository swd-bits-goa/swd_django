from django.shortcuts import render
from main.models import Leave, DayPass


# Create your views here.

def gate_security(request):
    leaves = Leave.objects.filter(approved=True)
    daypasss = DayPass.objects.filter(approved=True)
    context = {}
    found_leave = False
    if request.POST:
        username = request.POST.get('username')
        for leave in leaves:
            if username in leave.student.bitsId:
                student = leave.student
                found_leave = True
                if '1' in 'activate1':
                    leave.activated = True
                    leave.save()
                context = {
                    'student': student,
                    'leave': leave,
                    'found_leave': found_leave
                }
        for daypass in daypasss:
            if username in daypass.student.bitsId:
                student = daypass.student
                found_daypass = True
                if '2' in 'activate2':
                    daypass.activated = True
                    daypass.save()
                context = {
                    'student': student,
                    'daypass': daypass,
                    'found_daypass': found_daypass,
                    'found_leave': found_leave
                }

    return render(request, "gate_security.html", context)
