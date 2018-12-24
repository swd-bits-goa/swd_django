from django.http import HttpResponse

from .dev_info import messes

def index(request):
    from main.models import MessOption, Student
    from datetime import datetime
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    for username, mess, month, year in messes:
        print(username)
        date = datetime.strptime(month + ' ' + str(year), '%B %Y')
        date = date.replace(day=1)
        try:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            messoption = MessOption.objects.create(student=student, monthYear=date, mess = mess[0])
        except Exception as e:
            print(e)
    return HttpResponse("Success")
