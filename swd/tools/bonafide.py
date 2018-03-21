from .dev_info import bonafides

def index(request):
    from django.contrib.auth.models import User
    from main.models import Bonafide, Student
    from django.http import HttpResponse
    import datetime
    for idd, username, reason, other, year, branch1, branch2, gender, printed, count, date, dels  in bonafides:
        print(username, end='')
        try:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
<<<<<<< HEAD
            rev_date= datetime.datetime.strptime(date, '%B %d, %Y').date()
=======
            rev_date= datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
>>>>>>> 4066bce... Add scripts to import data after sanitization (#70)
            bonafide = Bonafide.objects.create(student=student, reason=reason, otherReason=other, reqDate=rev_date, printed=True if printed=='YES' else False)
            print('3')
            bonafide.save()
            print('pass')
        except Exception as e:
            print(e, '------------')
            print('fail')

    return HttpResponse("Done")
