from .dev_info import info 

def index(request):
    from main.models import Student
    import datetime
    for studentID, name, dob, sex, bloodgp, mobile, mail, alergies, fname, feepayingP, relation, pdob, psex, pmobno, plandline, pofficetel, pmail, hostel, hostelNo in info:
        print(studentID)
        try:
            student = Student.objects.get(bitsId=studentID)
            student.gender=sex
            rev_bDay = datetime.datetime.strptime(dob, '%d-%b-%y').strftime('%Y-%m-%d')
            student.bDay=rev_bDay
            student.phone=mobile
            student.email=mail
            student.bloodGroup=bloodgp
            student.parentName=fname if fname != '' else feepayingP
            student.parentPhone=pmobno
            student.parentEmail=pmail
            student.save()
            print('pass')
        except Exception as e:
            print(e)
            print('fail')