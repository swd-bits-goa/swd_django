from .dev_info import address

def index(request):
    from main.models import Student
    for bitsId, addr in address:
        print(bitsId)
        try:
            student = Student.objects.get(bitsId=bitsId)
            student.address = addr
            student.save()
            print('pass')
        except:
            print('fail')