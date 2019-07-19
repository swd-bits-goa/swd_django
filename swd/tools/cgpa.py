from django.http import HttpResponse

from .dev_info import cgpa

def index(request):
    from main.models import Student
    for bitsId, cg in cgpa:
        print(bitsId)
        try:
            student = Student.objects.get(bitsId=bitsId)
            student.cgpa = cg
            student.save()
            print('pass')
        except Exception as e:
            print(e)
            print('fail')

    return HttpResponse("Done")
